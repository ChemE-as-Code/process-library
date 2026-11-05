"""p-toluenesulfonyl-chloride-1 (#162): the folder's hand-written numbers against its own model.

Fast, without core: the flowsheet's calculated streams (written by cheme process propagate) and
the materials' molar masses and heat capacities are enough to check what the folder states by
hand (DESIGN.md D-004, D-007, D-009):

- the duties written as hand arithmetic (Q1, Q3, Q4, Q5 and its dilution share) follow from the
  streams they name;
- the feeds keep the patent's ratios per mol of toluene (1.5 + 1.5 mol ClSO3H, 0.45 mol NH4Cl);
- the yield on toluene and the product's assay stated in process.yaml and DESIGN.md hold;
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


def test_yield_and_assay_as_stated(model):
    materials, streams = model
    product = _kmol(model, "S24")
    para = product["PTSCL_S"] + product.get("PTSCL", 0.0)
    assert para / _kmol(model, "S4")["TOL"] == pytest.approx(0.788, abs=0.001)  # 78.8 % (D-005)
    mass = streams["S24"]["state"]["design"]["flow"]["value"]
    assay = para * materials["PTSCL"]["molar_mass"] / mass
    assert assay == pytest.approx(0.997, abs=0.0005)  # 99.7 wt% (D-002)
    assert "78.8 %" in (PROCESS / "process.yaml").read_text(encoding="utf-8")


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
