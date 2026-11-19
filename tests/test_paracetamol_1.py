"""paracetamol-1 (#481): the folder's stated numbers against its own files.

Fast, without core: scripts/balance.py is plain Python and repeats propagate's algebra
(DESIGN.md D-006), so the statements the folder makes in DESIGN.md, process.yaml and the
comments can be checked against it and against the flowsheet propagate wrote:

- the script's feeds and duties are the values the flowsheet cites (the balance-output
  contract, library ADR 0027) and its product agrees with propagate's;
- the Setschenow coefficient the crystallizers declare is the one calibrated to SRC-1
  Example 1, and the yield DESIGN.md states is the script's;
- the solubility points are SRC-3's mole fractions converted to kg per kg of water;
- the recipe's batch closes the flowsheet's product rate, and lca.yaml's carbon per batch and
  technology text follow the recipe;
- the entry is public with CC-BY-4.0 and its chemicals are in the registry.
"""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path

import pytest
import yaml

KIT = Path(__file__).resolve().parents[1]
PROCESS = KIT / "processes" / "paracetamol-1"


def _balance():
    spec = importlib.util.spec_from_file_location(
        "paracetamol_balance", PROCESS / "scripts" / "balance.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def solved():
    b = _balance()
    pap, s = b.solve()
    return b, pap, s


def _yaml(rel: str) -> dict:
    return yaml.safe_load((PROCESS / rel).read_text(encoding="utf-8"))


def _text(rel: str) -> str:
    return " ".join((PROCESS / rel).read_text(encoding="utf-8").split())


def _streams() -> dict:
    return {s["id"]: s for s in _yaml("process/flowsheet.yaml")["streams"]}


def _value(stream: dict, quantity: str) -> float:
    return stream["state"]["design"][quantity]["value"]


def _step(sid: str) -> dict:
    return next(s for s in _yaml("process/flowsheet.yaml")["steps"] if s["id"] == sid)


def test_feeds_and_duties_match_the_script(solved):
    b, _, s = solved
    streams = _streams()
    for sid in ("S1", "S2", "S4", "S11"):
        assert _value(streams[sid], "flow") == pytest.approx(sum(s[sid].values()), abs=0.01)
    q = b.duties(s)
    for sid in ("Q1", "Q2", "Q7", "Q8"):
        assert _value(streams[sid], "duty") == pytest.approx(q[sid], abs=0.01), sid


def test_script_batch_is_the_recipes_and_m101_times_fit(solved):
    """The per-batch heats use the recipe's batch; M-101's ASSUMED durations cover the script's
    jacket estimate (D-003), and the jacket area is the one the recipe gives R-101."""
    b, _, s = solved
    recipe = _yaml("process/recipe.yaml")
    assert b.BATCH_KG == pytest.approx(recipe["batch_size"]["value"])
    ops = {o["id"]: o for o in recipe["unit_procedures"][0]["operations"]}
    heat, cool = b.m101_times(s)
    assert heat <= ops["heat"]["duration"]["value"] < heat + 0.1
    assert cool <= ops["cool"]["duration"]["value"] < cool + 0.1
    # the polish loop is no hand-off: R-101 receives at M-101's transfer
    assert ops["polish"]["kind"] == "filter"
    assert [o["kind"] for o in ops.values()].count("transfer") == 1


def test_heats_moved_by_the_solid_basis_are_sized(solved):
    """D-005: the chilled water's net crystallisation heat is right to 0.3 kW; the redissolution
    and R-101's metal are in Q7, E-101 and D-101's cool-down in Q8 (D-009)."""
    b, _, s = solved
    q = b.duties(s)
    assert abs(q["CR101"] - q["Q3_over"]) < 0.5
    assert q["R101_metal"] == pytest.approx(315_000 / (b.BATCH_KG / b.CAPACITY) / 3600, rel=1e-3)
    assert b.vant_hoff() == pytest.approx(27.17, abs=0.005)
    design = _text("DESIGN.md")
    for fact in ("27.17 kJ/mol", "12.4 kW", "12.7 kW", "4.3 kW", "24.8 kW", "8.5 kW"):
        assert fact in design, fact
    assert f"{q['E101']:.1f} kW" == "24.8 kW" and f"{q['Q3_over']:.1f} kW" == "12.4 kW"


def test_script_product_agrees_with_propagate(solved):
    _, _, s = solved
    calculated = _value(_streams()["S15"], "flow")
    assert sum(s["S15"].values()) == pytest.approx(calculated, rel=2e-4)
    assert calculated == pytest.approx(2_000_000 / 7920, rel=2e-4)


def test_salting_in_is_the_calibrated_one(solved):
    b, _, _ = solved
    assert b.calibration() == pytest.approx(b.SALTING_HOAC, abs=5e-5)
    for sid in ("CR101", "W101"):
        coeff = _step(sid)["crystallizer"]["solubility"]["salting_out"]["coefficients"]
        assert coeff["HOAC"] == pytest.approx(b.SALTING_HOAC)


def test_solubility_points_are_src3_converted(solved):
    b, _, _ = solved
    mole_fractions = {293.15: 0.00152, 298.15: 0.00185, 303.15: 0.00209, 308.15: 0.00256, 313.15: 0.00315}
    for sid in ("CR101", "W101"):
        points = dict(map(tuple, _step(sid)["crystallizer"]["solubility"]["points"]))
        for t, x in mole_fractions.items():
            assert points[t] == pytest.approx(x / (1 - x) * b.MW["APAP"] / b.MW["H2O"], abs=2e-6)
    assert b.SOLUBILITY == pytest.approx(
        dict(map(tuple, _step("CR101")["crystallizer"]["solubility"]["points"]))[293.15]
    )


def test_yield_stated_in_design_and_manifest(solved):
    b, pap, s = solved
    product = s["S15"]
    yield_ = (product["APAP_S"] + product["APAP"]) / b.MW["APAP"] / pap
    stated = f"{100 * yield_:.1f} %"
    assert stated == "75.5 %"
    assert f"model's yield is {stated} of theory" in _text("DESIGN.md")
    assert f"the yield is {stated} of theory" in _text("process.yaml")
    # like for like with SRC-1 Example 4: the same plant crystallising at Example 1's temperature
    cold = b.plant(pap, b.T_EX1)["S15"]
    assert f"{100 * (cold['APAP_S'] + cold['APAP']) / b.MW['APAP'] / pap:.1f} %" == "81.6 %"
    assert "gives 81.6 %" in _text("DESIGN.md")


def test_calibration_at_the_examples_temperature(solved):
    """SRC-1 Example 1 isolates at 10 to 15 C: the calibration takes its mid-point, with the pure
    water's solubility extrapolated from SRC-3's 293.15 K point by van 't Hoff (D-007)."""
    b, _, _ = solved
    assert b.T_EX1 == 285.65
    assert b.solubility_at(b.T_EX1) == pytest.approx(0.009529, abs=1e-6)
    assert b.solubility_at(293.15) == b.SOLUBILITY


def test_recipe_batch_closes_the_flowsheet():
    recipe = _yaml("process/recipe.yaml")
    batch = recipe["batch_size"]["value"]
    rate = _value(_streams()["S15"], "flow")
    cycle = batch / rate
    assert cycle == pytest.approx(10.304, abs=0.002)
    batches = recipe["hours_per_year"]["value"] / cycle
    assert round(batches) == 769
    lca = _yaml("lca/lca.yaml")
    assert f"{batch:.2f} kg per batch, {round(batches)} batches a year" in lca["technology"]


def test_carbon_per_batch_follows_src1_and_the_recipe(solved):
    _, _, s = solved
    batch = _yaml("process/recipe.yaml")["batch_size"]["value"]
    hours = batch / _value(_streams()["S15"], "flow")
    consumables = {c["id"]: c for c in _yaml("lca/lca.yaml")["consumables"]}
    # SRC-1 Example 1 per 109 g of 4-aminophenol: 4.3 g carbon, 0.2 + 0.1 g hydrosulfite, 0.5 g sulfite
    for cid, grams in (("activated-carbon", 4.3), ("sodium-hydrosulfite", 0.3), ("sodium-sulfite", 0.5)):
        assert consumables[cid]["per_batch"] == pytest.approx(grams / 109.0 * s["S2"]["PAP"] * hours, abs=0.1), cid


def test_screening_numbers_are_recorded():
    text = _text("DESIGN.md")
    for fact in ("2.18 %", "313.6 K", "15.1 %", "317.1 K", "373.15 K"):
        assert fact in text
    hazard = _step("R101")["hazard"]
    assert hazard["mtt"] == 373.15


def test_core_screens_r101_as_recorded():
    """The screening values DESIGN.md D-011 states are core's, and the all-at-once rise adds the
    excess anhydride's hydrolysis to the largest single reaction's dT_ad."""
    pytest.importorskip("chemeascode")
    from chemeascode.domains.safety.reaction_hazards import screen

    report = screen(PROCESS)
    r101 = next(e for e in report.entries if e.node == "R101")
    assert r101.mtsr == pytest.approx(313.64, abs=0.01)
    assert r101.accumulation == pytest.approx(0.0218, abs=5e-5)
    assert r101.mtt == pytest.approx(373.15)
    design = _text("DESIGN.md")
    assert f"{100 * r101.accumulation:.2f} %" in design and f"{r101.mtsr:.1f} K" in design
    # 35.1 K (ACET) + 22.8 K (HYD, all 1.15 mol) x 0.15/1.15 = 38.1 K: the 330 K permissive keeps 5 K
    rise = 35.1 + 22.8 * 0.15 / 1.15
    assert 373.15 - (330.0 + rise) == pytest.approx(5.0, abs=0.1)
    assert "about 38 K" in design and "below 330 K" in design


def test_recipe_with_core_bottleneck_and_hand_off():
    pytest.importorskip("chemeascode")
    from chemeascode.domains.process.recipe import recipe_report

    result = recipe_report(PROCESS)
    assert not [f for f in result.findings if f.level in ("warning", "error")]
    cycles = {u.procedure if hasattr(u, "procedure") else u.label: u.cycle for u in result.units}
    react = max(result.units, key=lambda u: u.cycle)
    assert react.cycle == pytest.approx(10.304, abs=0.002)
    receive = next(s for s in result.steps if s.procedure == "REACT" and s.operation == "receive")
    handoff = next(s for s in result.steps if s.procedure == "DISSOLVE" and s.operation == "transfer")
    assert receive.start == pytest.approx(handoff.start)
    assert len(cycles) == 4


def test_public_and_registered():
    manifest = _yaml("process.yaml")
    assert manifest["publication"] == {"status": "public", "license": "CC-BY-4.0"}
    slugs = {c["slug"] for c in yaml.safe_load((KIT / "chemicals" / "chemicals.yaml").read_text())["chemicals"]}
    for side in ("inputs", "outputs", "utilities"):
        for flow in manifest["chemistry"][side]:
            assert flow["chemical"] in slugs, flow["chemical"]
    assert re.search(r"requires: cheme-as-code>=1\.12", (PROCESS / "plant.yaml").read_text())
