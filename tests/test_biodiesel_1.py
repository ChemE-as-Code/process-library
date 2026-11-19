"""biodiesel-1 (#515): the folder's stated numbers against its own flowsheet.

Fast and without core: the flowsheet's streams (propagated by core) are read as YAML, and the
statements the folder makes in DESIGN.md, README.md, process.yaml, lca/lca.yaml and the
benchmarks are checked against them:

- the specs hold: 32 420 t/a of biodiesel in 8000 h and 6 mol of methanol per mol of oil, and
  the followers sit at their stated ratios to the oil;
- the product meets the stated ASTM D6751 limits (total glycerol, water) and holds no methanol;
- the crude glycerol's stated composition, and the glycerol balance against the reactions'
  extent (TRANS 99.7 % overall);
- the methanol balance closes over fresh feed, reaction and losses, and the recycle is dry;
- the stated specific consumptions (unallocated) follow from the streams;
- the allocation shares are the products' masses;
- the hand duties' arithmetic in their sources is reproduced from the materials' heat capacities;
- every heat stream reaches the LCI, every vent source has an emission exclusion;
- the benchmark's crude glycerol range follows from the plant model's figures;
- the process is public with CC-BY-4.0 and requires cheme-as-code 1.12.
"""

from __future__ import annotations

import csv
from pathlib import Path

import pytest
import yaml

KIT = Path(__file__).resolve().parents[1]
PROCESS = KIT / "processes" / "biodiesel-1"


def _load(rel: str) -> dict:
    return yaml.safe_load((PROCESS / rel).read_text(encoding="utf-8"))


def _text(rel: str) -> str:
    return " ".join((PROCESS / rel).read_text(encoding="utf-8").split())


@pytest.fixture(scope="module")
def sheet() -> dict:
    return _load("process/flowsheet.yaml")


@pytest.fixture(scope="module")
def materials() -> dict[str, dict]:
    return {c["id"]: c for c in _load("process/materials.yaml")["components"]}


@pytest.fixture(scope="module")
def streams(sheet) -> dict[str, dict]:
    return {s["id"]: s["state"]["design"] for s in sheet["streams"] if "state" in s}


@pytest.fixture(scope="module")
def kg(streams, materials):
    """Component mass flows (kg/h) of a material stream, from its flow and composition."""

    def flows(sid: str) -> dict[str, float]:
        state = streams[sid]
        total = state["flow"]["value"]
        comp = state["composition"]
        values = comp["values"]
        if comp["basis"] == "mole_fraction":
            mass = {k: x * materials[k]["molar_mass"] for k, x in values.items()}
            s = sum(mass.values())
            values = {k: m / s for k, m in mass.items()}
        else:
            assert comp["basis"] == "mass_fraction"
        return {k: w * total for k, w in values.items()}

    return flows


def _flow(streams, sid: str) -> float:
    return streams[sid]["flow"]["value"]


def _duty(streams, sid: str) -> float:
    return streams[sid]["duty"]["value"]


def test_the_specs_hold(sheet, streams, kg, materials):
    assert _flow(streams, "S27") * 8000 / 1000 == pytest.approx(32420, rel=1e-5)
    tg = kg("S1")["TG"] / materials["TG"]["molar_mass"]
    meoh = kg("S5")["MEOH"] / materials["MEOH"]["molar_mass"]
    assert meoh / tg == pytest.approx(6.0, rel=1e-5)
    rate = next(s for s in sheet["specs"] if s["id"] == "rate")
    oil = _flow(streams, "S1")
    for sid, ratio in rate["vary"]["with"].items():
        assert _flow(streams, sid) == pytest.approx(ratio * oil, rel=1e-5)
    # the catalyst ratio is 0.25 wt% methoxide on the oil as a 25 wt% solution (D-005)
    assert kg("S4")["NAOME"] / oil == pytest.approx(0.0025, rel=1e-6)


def test_the_capacity_arithmetic():
    # 9.8 million US gallons at 0.8739 kg/L (D-002)
    assert 9.8e6 * 3.785412 * 0.8739 / 1000 == pytest.approx(32420, rel=1e-4)
    assert "32 420 t/a" in _text("DESIGN.md")


def test_the_product_meets_the_stated_limits(kg, materials, streams):
    p = kg("S27")
    total = _flow(streams, "S27")
    bound = p["TG"] * materials["GLY"]["molar_mass"] / materials["TG"]["molar_mass"]
    total_glycerol = (bound + p.get("GLY", 0.0)) / total
    assert total_glycerol < 0.0024  # ASTM D6751 0.240 wt% (SRC-1 p. 23)
    assert round(100 * total_glycerol, 3) == pytest.approx(0.032, abs=0.0015)
    assert round(100 * p["H2O"] / total, 3) == pytest.approx(0.023, abs=0.0015)
    assert round(100 * p["FAME"] / total, 2) == pytest.approx(99.68, abs=0.01)
    assert p.get("MEOH", 0.0) == 0.0
    assert "99.68 wt%" in _text("process.yaml")


def test_the_crude_glycerol_and_the_glycerol_balance(kg, materials, streams):
    c = kg("S32")
    total = _flow(streams, "S32")
    assert round(100 * c["GLY"] / total, 1) == pytest.approx(86.6)
    assert round(100 * c["FAME"] / total, 1) == pytest.approx(8.0)
    assert round(100 * c["H2O"] / total, 1) == pytest.approx(2.9)
    assert round(100 * c["NACL"] / total, 1) == pytest.approx(2.2)
    assert "86.6 wt% glycerol" in _text("DESIGN.md")
    # glycerol formed (extent of TRANS) = what leaves in the crude, the wash water and the product
    tg_in = kg("S1")["TG"] / materials["TG"]["molar_mass"]
    tg_out = kg("S27")["TG"] / materials["TG"]["molar_mass"]
    formed = (tg_in - tg_out) * materials["GLY"]["molar_mass"]
    out = c["GLY"] + kg("S22").get("GLY", 0.0) + kg("S27").get("GLY", 0.0)
    assert out == pytest.approx(formed, rel=1e-4)
    assert 1 - tg_out / tg_in == pytest.approx(1 - 0.10 * 0.03, rel=1e-6)  # 99.7 % overall


def test_the_methanol_balance_and_the_dry_recycle(kg, materials):
    mw = materials["MEOH"]["molar_mass"]
    fresh = kg("S3")["MEOH"] + kg("S4")["MEOH"]
    tg_in = kg("S1")["TG"] / materials["TG"]["molar_mass"]
    tg_out = kg("S27")["TG"] / materials["TG"]["molar_mass"]
    consumed = 3 * (tg_in - tg_out) * mw
    naome = kg("S4")["NAOME"] / materials["NAOME"]["molar_mass"]
    formed = naome * mw  # NEUT is complete in the wash and the neutraliser
    lost = kg("S22").get("MEOH", 0.0) + kg("S25").get("MEOH", 0.0) + kg("S32").get("MEOH", 0.0)
    assert fresh + formed == pytest.approx(consumed + lost, abs=0.05)
    for sid in ("S15", "S17", "S20"):
        assert set(k for k, v in kg(sid).items() if v > 0) == {"MEOH"}


def test_the_stated_specific_consumptions(streams, kg):
    bd = _flow(streams, "S27")
    assert _flow(streams, "S1") / bd == pytest.approx(1.005, abs=0.0005)
    assert _flow(streams, "S3") / bd == pytest.approx(0.1006, abs=0.00005)
    assert (kg("S3")["MEOH"] + kg("S4")["MEOH"]) / bd == pytest.approx(0.1081, abs=0.00005)
    assert _flow(streams, "S23") / bd == pytest.approx(1.145, abs=0.0005)
    assert _flow(streams, "S32") / bd == pytest.approx(0.120, abs=0.0005)
    steam = sum(_duty(streams, q) for q in ("Q1", "Q2", "Q3", "Q6", "Q10"))
    power = sum(_duty(streams, p) for p in ("P1", "P2", "P3", "P4"))
    cw = sum(_duty(streams, q) for q in ("Q4", "Q5", "Q7", "Q8", "Q9", "Q11", "Q12"))
    assert steam / bd == pytest.approx(0.134, abs=0.0005)
    assert power / bd == pytest.approx(0.0173, abs=0.00005)
    assert cw / bd == pytest.approx(0.120, abs=0.0005)
    readme = _text("README.md")
    for stated in ("1.005 kg of oil", "0.134 kWh of LP-steam heat", "0.017 kWh of power", "1.15 kg of wash water"):
        assert stated in readme


def test_the_allocation_shares_are_the_product_masses(streams):
    alloc = _load("lca/lca.yaml")["allocation"]
    bd, cg = _flow(streams, "S27"), _flow(streams, "S32")
    assert alloc["shares"]["BD"] == pytest.approx(bd / (bd + cg), abs=5e-5)
    assert alloc["shares"]["CGLY"] == pytest.approx(cg / (bd + cg), abs=5e-5)
    assert sum(alloc["shares"].values()) == pytest.approx(1.0)


def test_the_hand_duties_follow_from_the_heat_capacities(kg, materials, streams):
    def cap(sid: str) -> float:  # kJ/(h K)
        return sum(m / materials[k]["molar_mass"] * materials[k]["liquid_heat_capacity"] for k, m in kg(sid).items())

    n15 = kg("S15")["MEOH"] / materials["MEOH"]["molar_mass"]
    n17 = kg("S17")["MEOH"] / materials["MEOH"]["molar_mass"]
    nw = kg("S25")["H2O"] / materials["H2O"]["molar_mass"]
    cp_m = materials["MEOH"]["liquid_heat_capacity"]
    q3 = (cap("S13") * 30 + n15 * 36317) / 3600
    q6 = (cap("S21") * 35 + nw * 43092 + kg("S25").get("MEOH", 0.0) / 32.042 * 36317) / 3600
    q8 = cap("S26") * 55 / 3600
    q10 = (2 * n17 * 35281 + cap("S31") * 60 + n17 * cp_m * 4.45) / 3600
    q11 = (2 * n17 * 35281 + n17 * cp_m * 29.45) / 3600
    q12 = cap("S31") * 80 / 3600
    for sid, value in (("Q3", q3), ("Q6", q6), ("Q8", q8), ("Q10", q10), ("Q11", q11), ("Q12", q12)):
        assert _duty(streams, sid) == pytest.approx(value, abs=0.1), sid


def test_the_model_duties_are_cores(streams):
    for q in ("Q1", "Q2", "Q5", "Q9"):
        assert streams[q]["duty"]["provenance"] == "calculated"
        assert streams[q]["duty"]["source"].startswith("cheme process propagate: conversion duty")


def test_every_heat_stream_reaches_the_lci(streams):
    rows = {r["key"]: r for r in csv.DictReader((PROCESS / "lca" / "inventory.csv").open(encoding="utf-8"))}
    steam = rows["feed:LPS"]["streams"].split()
    cw = rows["product:CW"]["streams"].split()
    assert sorted(steam) == sorted(["Q1", "Q2", "Q3", "Q6", "Q10"])
    assert sorted(cw) == sorted(["Q4", "Q5", "Q7", "Q8", "Q9", "Q11", "Q12"])
    assert float(rows["feed:LPS"]["plant"]) == pytest.approx(sum(_duty(streams, q) for q in steam), abs=0.01)


def test_every_vessel_with_methanol_has_an_emission_exclusion():
    excluded = {tag for e in _load("lca/lca.yaml")["emission_exclusions"] for tag in e["equipment"]}
    for tag in ("V-101", "V-501", "E-201", "D-204", "R-101", "R-102", "R-302", "V-301"):
        assert tag in excluded


def test_the_crude_glycerol_benchmark_follows_from_the_plant_model():
    data = yaml.safe_load((KIT / "benchmarks" / "bio-based-chemicals.yaml").read_text(encoding="utf-8"))
    ref = data["kpis"]["biodiesel-crude-glycerol"]["references"][0]
    biodiesel_t = 9.8e6 * 3.785412 * 0.8739 / 1000
    lo, hi = ref["range"]
    assert lo == pytest.approx(4380 * 0.90718474 / biodiesel_t, abs=5e-5)
    assert hi == pytest.approx(4380 / biodiesel_t, abs=5e-5)
    binding = next(d for d in data["datasets"] if d["process"] == "biodiesel-1")
    dataset = _load("lca/dataset.yaml")
    assert binding["dataset"] == dataset["id"]


def test_published_public_with_cc_by():
    pub = _load("process.yaml")["publication"]
    assert pub == {"status": "public", "license": "CC-BY-4.0"}


def test_requires_core_1_12():
    assert _load("plant.yaml")["requires"] == "cheme-as-code>=1.12"
