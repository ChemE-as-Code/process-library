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
- the MTT is where VCM's and water's vapour pressures reach the stated relief set pressure
  (recomputed with the `chemicals` package, no thermo needed);
- the heat-up's time and Q1 are the charge's, the jacket the patent's demonstrated duty;
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


CYCLE_H = 8000 / 4178.6368  # cheme process recipe: 4178.6 batches in 8000 h (7.658 h per autoclave, four autoclaves)
HEAT_UP_H = 0.946  # process/recipe.yaml, by hand (D-003, L-6)


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
    assert capacity == pytest.approx(174_642, rel=1e-3)
    assert "174.6 kt/a" in _text("process.yaml")
    assert "175 kt/a" in _text("README.md")
    up = recipe["unit_procedures"][0]
    assert up["parallel"] == 4 and up["vessel"]["volume"] == 130


def test_resin_keeps_less_vcm_than_the_ecvm_limit(streams) -> None:
    stripped = _mass(streams["S13"])
    assert stripped["VCM"] / stripped["PVC"] * 1e6 < 1.0  # g per t of resin, D-007


def test_mtt_is_the_relief_set_pressure_on_the_vapour_pressures(sheet) -> None:
    r101 = next(s for s in sheet["steps"] if s["id"] == "R101")
    mtt = r101["hazard"]["mtt"]
    assert mtt == pytest.approx(357.10, abs=0.01)
    # the stated values: VCM 1644 kPa and water 56 kPa add up to the relief set pressure
    assert 1644 + 56 == 1700
    assert "relief set at 1700 kPa(a)" in _text("equipment/equipment-list.yaml")
    assert "VCM 1644 kPa and water 56 kPa at 357.10 K" in _text("DESIGN.md")
    # and recomputed with the `chemicals` package the library's tests install (the coefficients
    # thermo's DIPPR_PERRY_8E method and its IAPWS_PSAT water line use, SRC-6)
    from chemicals.dippr import EQ101
    from chemicals.iapws import iapws95_Psat
    from chemicals.vapor_pressure import Psat_data_Perrys2_8

    c = Psat_data_Perrys2_8.loc["75-01-4"]
    vcm = EQ101(mtt, c["C1"], c["C2"], c["C3"], c["C4"], c["C5"])
    assert vcm / 1e3 == pytest.approx(1644, rel=1e-3)
    assert iapws95_Psat(mtt) / 1e3 == pytest.approx(56, rel=1e-2)
    assert (vcm + iapws95_Psat(mtt)) / 1e3 == pytest.approx(1700, rel=2e-3)


def test_heat_up_is_the_charges_not_the_end_contents(recipe, sheet) -> None:
    """The heat-up's time and Q1 by hand from the charge (core 0e85885 heats the end-of-batch
    content when nothing is dosed, L-6): the charge's components over 32 K, with the metal."""
    mat = {c["id"]: c for c in _load("process/materials.yaml")["components"]}
    kmol = {"VCM": 46_300 / MW["VCM"], "H2O": 56_800 / MW["H2O"]}
    charge = sum(n * mat[k]["liquid_heat_capacity"] for k, n in kmol.items())  # kJ/K
    assert charge == pytest.approx(313_356, rel=5e-4)  # with the additives, D-003
    vessel = recipe["unit_procedures"][0]["vessel"]
    jacket, metal = vessel["jacket"], vessel["metal_heat_capacity"]
    ua = jacket["u"] * jacket["area"] / 1000  # kW/K
    hours = (313_356 + metal) / ua * math.log((353.15 - 298.15) / (353.15 - 330.15)) / 3600
    assert hours == pytest.approx(HEAT_UP_H, abs=5e-4)
    heat = next(op for op in recipe["unit_procedures"][0]["operations"] if op["id"] == "heat")
    assert heat["duration"]["value"] == HEAT_UP_H and "temperatures" not in heat
    q1 = next(s for s in sheet["streams"] if s["id"] == "Q1")["state"]["design"]["duty"]["value"]
    assert q1 == pytest.approx((313_356 + metal) * 32 / 1000 / CYCLE_H / 3.6, rel=1e-3)
    # the jacket and baffles remove what the patent's Table 1 reports for them at 80 % (3889 kW)
    assert ua * (330.15 - jacket["coolant_temperature"]) == pytest.approx(14_000 / 3.6, rel=2e-3)


def test_lci_specifics_are_the_stated_ones() -> None:
    with (PROCESS / "lca" / "inventory.csv").open(encoding="utf-8") as fh:
        per_fu = {row["key"]: float(row["quantity"]) for row in csv.DictReader(fh)}
    assert per_fu["feed:VCMF"] == pytest.approx(0.997, abs=6e-4)
    assert per_fu["feed:POWER"] == pytest.approx(0.139, abs=5e-4)
    assert per_fu["feed:LSTM"] == pytest.approx(0.170, abs=6e-4)
    assert per_fu["feed:LPS"] == pytest.approx(0.434, abs=6e-4)
    assert per_fu["product:WW"] == pytest.approx(1.28, abs=6e-3)
    assert per_fu["product:CHW"] == pytest.approx(0.452, abs=6e-4)
    assert per_fu["emission:VCM"] * 1e6 == pytest.approx(0.16, abs=6e-3)  # g per t
    # steam: LP heat at about 2.12 MJ/kg plus the live steam, about 0.91 t/t (BREF example 0.879)
    steam = per_fu["feed:LPS"] * 3.6 / 2.12 + per_fu["feed:LSTM"]
    assert steam == pytest.approx(0.91, abs=0.02)
    for text in (_text("README.md"), _text("DESIGN.md")):
        assert "0.91 t" in text and "139 kWh/t" in text and "1.28 t" in text
    assert "0.16 g per t" in _text("lca/lca.yaml")


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
