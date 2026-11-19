"""pvc-1 (#461): the folder's stated numbers against its own files.

Fast and without core: the flowsheet's streams (propagated by core), the recipe, the reactions,
the LCI inventory and the benchmarks are read as YAML or CSV, and the statements the folder
makes in DESIGN.md, README.md and process.yaml are checked against them:

- the charge follows US 6 825 288 B2, Example 1 (46.3 t VCM, 56.8 t water per batch) over the
  recipe's cycle, and the fresh VCM is the charge less the recovered VCM;
- R101 converts 90 % of the VCM and its duty is the heat of polymerisation (1539.7 kJ/kg);
- the heat of polymerisation is the patent's 368 kcal/kg, the activation energy the open
  kinetic scheme's;
- the recipe's batch size equals the dried resin over the cycle, the stated capacity follows;
- the resin keeps less VCM than the ECVM limit the BREF quotes (1 g/t);
- the MTT is where VCM's and water's vapour pressures reach the stated relief set pressure;
- the LCI's specific consumptions are those README.md and DESIGN.md state; the steam and
  wastewater cross-checks against the BREF;
- every flow of the inventory has a background or a recorded gap;
- the benchmarks name this dataset;
- the process is public with CC-BY-4.0 and requires cheme-as-code 1.12.
"""

from __future__ import annotations

import csv
import math
from pathlib import Path

import pytest
import yaml

KIT = Path(__file__).resolve().parents[1]
PROCESS = KIT / "processes" / "pvc-1"
MW = {"VCM": 62.496, "H2O": 18.015, "PVC": 62.496, "PVA": 44.053, "INIT": 346.464, "STOP": 586.766}


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


def _mass(state: dict) -> dict[str, float]:
    """kg/h of each component of a stream's design state."""
    flow = state["flow"]["value"]
    comp = state["composition"]
    if comp["basis"] == "mass_fraction":
        return {k: flow * w for k, w in comp["values"].items()}
    m = {k: x * MW[k] for k, x in comp["values"].items()}
    total = sum(m.values())
    return {k: flow * v / total for k, v in m.items()}


@pytest.fixture(scope="module")
def recipe() -> dict:
    return _load("process/recipe.yaml")


CYCLE_H = 7.7860916 / 4  # cheme process recipe: one autoclave's occupancy over four autoclaves


def test_charge_follows_the_patent_example_over_the_cycle(streams) -> None:
    charge = _mass(streams["S6"])
    assert charge["VCM"] * CYCLE_H == pytest.approx(46_300, rel=2e-4)
    assert charge["H2O"] * CYCLE_H == pytest.approx(56_800, rel=2e-4)
    assert streams["S3"]["flow"]["value"] * CYCLE_H == pytest.approx(22.2, rel=1e-3)
    assert streams["S4"]["flow"]["value"] * CYCLE_H == pytest.approx(22.5, rel=1e-3)
    assert streams["S8"]["flow"]["value"] * CYCLE_H == pytest.approx(44.7, rel=1e-3)
    # fresh VCM = the charge less the recovered VCM
    assert _mass(streams["S1"])["VCM"] + _mass(streams["S17"])["VCM"] == pytest.approx(charge["VCM"], rel=1e-5)
    assert _mass(streams["S1"])["VCM"] * CYCLE_H == pytest.approx(41_680, rel=2e-4)


def test_r101_converts_90_percent_and_its_duty_is_the_heat_of_polymerisation(sheet, streams) -> None:
    vcm_in, vcm_out = _mass(streams["S6"])["VCM"], _mass(streams["S7"])["VCM"]
    assert 1 - vcm_out / vcm_in == pytest.approx(0.90, abs=1e-5)
    q2 = next(s for s in sheet["streams"] if s["id"] == "Q2")["state"]["design"]["duty"]
    assert q2["provenance"] == "calculated"
    heat_kw = (vcm_in - vcm_out) * 1539.7 / 3600
    assert q2["value"] == pytest.approx(heat_kw, rel=2e-3)
    assert q2["value"] * CYCLE_H * 3.6 == pytest.approx(64_160, rel=3e-3)  # MJ per batch, D-008


def test_heat_of_polymerisation_and_activation_energy() -> None:
    poly = _load("process/reactions.yaml")["reactions"][0]
    assert poly["heat_of_reaction"]["value"] == pytest.approx(-368 * 4.184 * 62.496, abs=2)
    assert poly["rate"]["k"]["Ea"] == pytest.approx(8.314 * (3320 + (15460 - 2190) / 2), abs=1)
    k330 = poly["rate"]["k"]["A"] * math.exp(-poly["rate"]["k"]["Ea"] / (8.314 * 330.15))
    assert k330 == pytest.approx(4.86e-4, rel=2e-3)


def test_recipe_batch_size_is_the_resin_over_the_cycle(streams, recipe) -> None:
    resin = streams["S23"]["flow"]["value"]
    assert recipe["batch_size"]["value"] == pytest.approx(resin * CYCLE_H, rel=1e-3)
    capacity = recipe["batch_size"]["value"] * recipe["hours_per_year"]["value"] / CYCLE_H / 1000
    assert capacity == pytest.approx(171_769, rel=1e-3)
    assert "171.8 kt/a" in _text("process.yaml")
    assert "172 kt/a" in _text("README.md")
    up = recipe["unit_procedures"][0]
    assert up["parallel"] == 4 and up["vessel"]["volume"] == 130


def test_resin_keeps_less_vcm_than_the_ecvm_limit(streams) -> None:
    stripped = _mass(streams["S13"])
    assert stripped["VCM"] / stripped["PVC"] * 1e6 < 1.0  # g per t of resin, D-007


def test_mtt_is_the_relief_set_pressure_on_the_vapour_pressures(sheet) -> None:
    r101 = next(s for s in sheet["steps"] if s["id"] == "R101")
    mtt = r101["hazard"]["mtt"]
    assert mtt == pytest.approx(357.10, abs=0.01)
    try:
        from thermo import VaporPressure
    except ImportError:
        pytest.skip("thermo not installed")
    vcm = VaporPressure(CASRN="75-01-4")
    vcm.method = "DIPPR_PERRY_8E"
    water = VaporPressure(CASRN="7732-18-5")
    assert (vcm(mtt) + water(mtt)) / 1e3 == pytest.approx(1700, rel=2e-3)


def test_lci_specifics_are_the_stated_ones() -> None:
    with (PROCESS / "lca" / "inventory.csv").open(encoding="utf-8") as fh:
        per_fu = {row["key"]: float(row["quantity"]) for row in csv.DictReader(fh)}
    assert per_fu["feed:VCMF"] == pytest.approx(0.997, abs=6e-4)
    assert per_fu["feed:POWER"] == pytest.approx(0.139, abs=5e-4)
    assert per_fu["feed:LSTM"] == pytest.approx(0.179, abs=6e-4)
    assert per_fu["product:WW"] == pytest.approx(1.29, abs=6e-3)
    assert per_fu["product:CHW"] == pytest.approx(0.440, abs=6e-4)
    # steam: LP heat at about 2.12 MJ/kg plus the live steam, about 0.90 t/t (BREF example 0.879)
    steam = per_fu["feed:LPS"] * 3.6 / 2.12 + per_fu["feed:LSTM"]
    assert steam == pytest.approx(0.90, abs=0.02)
    for text in (_text("README.md"), _text("DESIGN.md")):
        assert "0.90 t" in text and "139 kWh/t" in text


def test_every_inventory_flow_has_a_background_or_a_gap() -> None:
    lca = _load("lca/lca.yaml")
    keys = {f["key"] for f in lca["flows"]}
    with (PROCESS / "lca" / "inventory.csv").open(encoding="utf-8") as fh:
        flows = {row["key"] for row in csv.DictReader(fh)}
    assert flows - {"product:PVCP"} <= keys


def test_benchmarks_name_this_dataset() -> None:
    bench = yaml.safe_load((KIT / "benchmarks" / "polymers.yaml").read_text(encoding="utf-8"))
    dataset = _load("lca/dataset.yaml")["id"]
    entry = next(d for d in bench["datasets"] if d["process"] == "pvc-1")
    assert entry["dataset"] == dataset
    assert set(entry["kpis"]) == {"pvc-specific-electricity", "pvc-specific-wastewater"}


def test_public_and_required_core() -> None:
    manifest = _load("process.yaml")
    assert manifest["publication"] == {"status": "public", "license": "CC-BY-4.0"}
    assert manifest["maturity"] == "concept"
    assert _load("plant.yaml")["requires"] == "cheme-as-code>=1.12"
