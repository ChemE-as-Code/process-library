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
    assert _value(streams["Q1"], "duty") == pytest.approx(q["Q1"], abs=0.01)
    assert _value(streams["Q2"], "duty") == pytest.approx(q["Q2"], abs=0.01)


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
    assert stated == "82.0 %"
    assert f"model's yield is {stated} of theory" in _text("DESIGN.md")
    assert f"the yield is {stated} of theory" in _text("process.yaml")


def test_recipe_batch_closes_the_flowsheet():
    recipe = _yaml("process/recipe.yaml")
    batch = recipe["batch_size"]["value"]
    rate = _value(_streams()["S15"], "flow")
    cycle = batch / rate
    assert cycle == pytest.approx(9.965, abs=0.002)
    batches = recipe["hours_per_year"]["value"] / cycle
    assert round(batches) == 795
    lca = _yaml("lca/lca.yaml")
    assert f"{batch:.2f} kg per batch, {round(batches)} batches a year" in lca["technology"]


def test_carbon_per_batch_follows_src1_and_the_recipe(solved):
    _, _, s = solved
    batch = _yaml("process/recipe.yaml")["batch_size"]["value"]
    hours = batch / _value(_streams()["S15"], "flow")
    carbon = 4.3 / 109.0 * s["S2"]["PAP"] * hours
    consumable = next(c for c in _yaml("lca/lca.yaml")["consumables"] if c["id"] == "activated-carbon")
    assert consumable["per_batch"] == pytest.approx(carbon, abs=0.1)


def test_screening_numbers_are_recorded():
    text = _text("DESIGN.md")
    for fact in ("2.18 %", "313.6 K", "15.1 %", "317.1 K", "373.15 K"):
        assert fact in text
    hazard = _step("R101")["hazard"]
    assert hazard["mtt"] == 373.15


def test_public_and_registered():
    manifest = _yaml("process.yaml")
    assert manifest["publication"] == {"status": "public", "license": "CC-BY-4.0"}
    slugs = {c["slug"] for c in yaml.safe_load((KIT / "chemicals" / "chemicals.yaml").read_text())["chemicals"]}
    for side in ("inputs", "outputs", "utilities"):
        for flow in manifest["chemistry"][side]:
            assert flow["chemical"] in slugs, flow["chemical"]
    assert re.search(r"requires: cheme-as-code>=1\.12", (PROCESS / "plant.yaml").read_text())
