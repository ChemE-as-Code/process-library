"""biodiesel-1 (#515): the folder's stated numbers against its own flowsheet.

Fast and without core: the flowsheet's streams (propagated by core) are read as YAML, and the
statements the folder makes in DESIGN.md, README.md, process.yaml, lca/lca.yaml and the
benchmarks are checked against them:

- the specs hold: 32 420 t/a of biodiesel in 8000 h and 6 mol of methanol per mol of oil, and
  the followers sit at their stated ratios to the oil;
- the product meets the stated ASTM D6751 limits (total glycerol, water) and holds no methanol;
- the crude glycerol's stated composition, and the glycerol balance against the reactions'
  extent (TRANS 99.7 % overall); the neutraliser leaves no free acid;
- the second decanter splits the methanol at the first one's distribution coefficient, and the
  flash leaves the methanol fraction its equilibrium allows;
- each steam-heated step's process temperature is within its steam's reach;
- the methanol balance closes over fresh feed, reaction and losses, and the recycle is dry;
- the stated specific consumptions (unallocated) follow from the streams;
- the allocation shares are the products' masses;
- the hand duties' arithmetic in their sources is reproduced from the materials' heat capacities,
  and each heater and condenser pair closes its step's energy balance;
- every heat stream reaches the LCI, the oil's carbon is biogenic, and every vessel, reactor or
  column that holds methanol has an emission exclusion;
- the benchmark's crude glycerol range follows from the plant model's figures;
- the process is public with CC-BY-4.0 and requires cheme-as-code 1.12.
"""

from __future__ import annotations

import csv
import json
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


def test_the_capacity_arithmetic(sheet):
    # 9.8 million US gallons (SRC-2 p. 9) at the density stated in D-002, against the recorded
    # capacity of the design basis and of the flowsheet's rate spec
    design = _text("DESIGN.md")
    density = float(design.split("x 3.785412 L x ")[1].split(" kg/L")[0])
    assert density == 0.8739
    capacity = 9.8e6 * 3.785412 * density / 1000
    basis = _load("process/design-basis.yaml")["capacity"]
    rate = next(s for s in sheet["specs"] if s["id"] == "rate")["target"]
    assert basis["biodiesel_t_per_year"] == pytest.approx(capacity, rel=1e-4)
    assert rate["value"] == basis["biodiesel_t_per_year"]
    assert rate["hours"] == basis["operating_hours_per_year"]
    assert basis["biodiesel_kg_per_h"] == pytest.approx(rate["value"] * 1000 / rate["hours"], rel=1e-6)
    assert "32 420 t/a" in design


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
    assert round(100 * c["GLY"] / total, 1) == pytest.approx(86.8)
    assert round(100 * c["FAME"] / total, 1) == pytest.approx(8.0)
    assert round(100 * c["H2O"] / total, 1) == pytest.approx(2.8)
    assert round(100 * c["NACL"] / total, 1) == pytest.approx(2.2)
    assert round(100 * c["MEOH"] / total, 2) == pytest.approx(0.17)
    assert c.get("HCL", 0.0) < 1e-3  # kg/h; dosed equal to the methoxide: no free acid (D-008)
    assert "86.8 wt% glycerol" in _text("DESIGN.md")
    assert "about 87 wt%" in next(p["title"] for p in _load("process/flowsheet.yaml")["products"] if p["id"] == "CGLY")
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
    assert _flow(streams, "S3") / bd == pytest.approx(0.1043, abs=0.00005)
    assert (kg("S3")["MEOH"] + kg("S4")["MEOH"]) / bd == pytest.approx(0.1118, abs=0.00005)
    assert _flow(streams, "S23") / bd == pytest.approx(1.145, abs=0.0005)
    assert _flow(streams, "S32") / bd == pytest.approx(0.120, abs=0.0005)
    lps = sum(_duty(streams, q) for q in ("Q1", "Q3", "Q5", "Q6"))
    mps = _duty(streams, "Q10")
    power = sum(_duty(streams, p) for p in ("P1", "P2", "P3", "P4", "P5", "P6"))
    cw = sum(_duty(streams, q) for q in ("Q2", "Q4", "Q7", "Q8", "Q9", "Q11", "Q12"))
    assert lps / bd == pytest.approx(0.124, abs=0.0005)
    assert mps / bd == pytest.approx(0.032, abs=0.0005)
    assert power / bd == pytest.approx(0.0183, abs=0.00005)
    assert cw / bd == pytest.approx(0.096, abs=0.0005)
    readme = _text("README.md")
    for stated in (
        "1.005 kg of oil",
        "0.124 kWh of LP-steam heat",
        "0.032 kWh of MP-steam heat",
        "0.018 kWh of power",
        "1.15 kg of wash water",
    ):
        assert stated in readme


def test_the_allocation_shares_are_the_product_masses(streams):
    alloc = _load("lca/lca.yaml")["allocation"]
    bd, cg = _flow(streams, "S27"), _flow(streams, "S32")
    assert alloc["shares"]["BD"] == pytest.approx(bd / (bd + cg), abs=5e-5)
    assert alloc["shares"]["CGLY"] == pytest.approx(cg / (bd + cg), abs=5e-5)
    assert sum(alloc["shares"].values()) == pytest.approx(1.0)


def test_the_hand_duties_follow_from_the_heat_capacities(kg, materials, streams):
    """The sources' arithmetic, with SRC-3's latent heats and vapour heat capacities (J/mol)."""

    def cap(sid: str) -> float:  # kJ/(h K)
        return sum(m / materials[k]["molar_mass"] * materials[k]["liquid_heat_capacity"] for k, m in kg(sid).items())

    def n(sid: str, k: str) -> float:  # kmol/h
        return kg(sid).get(k, 0.0) / materials[k]["molar_mass"]

    cp_m = materials["MEOH"]["liquid_heat_capacity"]
    t_dew = 315.73  # methanol at 40 kPa(a), the flash and the column (SRC-3)
    t_w = 318.96  # water at 10 kPa(a), the dryer (SRC-3)
    q4 = n("S15", "MEOH") * (47.26 * (373.15 - t_dew) + 36550 + cp_m * (t_dew - 308.15)) / 3600
    q3 = q4 + (cap("S16") * 40 - cap("S15") * 25) / 3600
    q7 = (
        n("S25", "H2O") * (33.84 * (368.15 - t_w) + 43092)
        + n("S25", "MEOH") * (47.19 * (368.15 - t_w) + 36370)
        + cap("S25") * (t_w - 308.15)
    ) / 3600
    q6 = q7 + (cap("S26") * 35 - cap("S25") * 25) / 3600
    q8 = cap("S26") * 55 / 3600
    q11 = n("S17", "MEOH") * (2 * 36550 + cp_m * (t_dew - 308.15)) / 3600
    t_reb = streams["S31"]["temperature"]["value"]
    q10 = q11 + (cap("S31") * (t_reb - 333.15) - cap("S17") * 25) / 3600
    q12 = cap("S31") * (t_reb - 313.15) / 3600
    for sid, value in (("Q3", q3), ("Q4", q4), ("Q6", q6), ("Q7", q7), ("Q8", q8), ("Q10", q10), ("Q11", q11), ("Q12", q12)):
        assert _duty(streams, sid) == pytest.approx(value, abs=0.1), sid


def test_each_heater_and_condenser_close_their_step(kg, materials, streams):
    """Heater minus condenser = the net enthalpy change of the step's liquids (D-009)."""

    def cap(sid: str) -> float:
        return sum(m / materials[k]["molar_mass"] * materials[k]["liquid_heat_capacity"] for k, m in kg(sid).items())

    def t(sid: str) -> float:
        return streams[sid]["temperature"]["value"]

    for heat, cond, feed, outs in (
        ("Q3", "Q4", "S13", ("S15", "S16")),
        ("Q6", "Q7", "S21", ("S25", "S26")),
        ("Q10", "Q11", "S30", ("S17", "S31")),
    ):
        net = sum(cap(o) * (t(o) - t(feed)) for o in outs) / 3600
        assert _duty(streams, heat) - _duty(streams, cond) == pytest.approx(net, abs=0.15), heat


def test_the_decanters_and_the_flash_split_methanol_consistently(kg, materials, streams):
    def w(sid: str) -> float:
        flows = kg(sid)
        return flows["MEOH"] / sum(flows.values())

    k1 = w("S10") / w("S9")
    k2 = w("S14") / w("S13")
    assert k1 == pytest.approx(5.4, abs=0.05)
    assert k2 == pytest.approx(k1, rel=2e-3)  # D-006: the coefficient held constant
    # D-007: one equilibrium stage at 373.15 K and 40 kPa(a), x = 40 / (2.933 x 353.7)
    x16 = streams["S16"]["composition"]["values"]["MEOH"]
    assert x16 == pytest.approx(40 / (2.933 * 353.7), rel=2e-3)
    assert streams["S16"]["temperature"]["value"] == 373.15
    assert streams["S16"]["pressure"]["value"] == 40


def test_the_steam_reaches_each_heated_step(sheet, streams):
    """A steam's supply temperature less its minimum approach covers the process temperature."""
    utilities = {f["id"]: f["utility"] for f in sheet["feeds"] if f.get("category") == "utility" and f["utility"]["kind"] == "steam"}
    hot = {"Q1": "S8", "Q3": "S16", "Q5": "S19", "Q6": "S26", "Q10": "S31"}
    energy = {s["id"]: s for s in sheet["streams"] if s.get("kind") == "energy"}
    for q, sid in hot.items():
        u = utilities[energy[q]["from"].split(".")[0]]
        assert u["supply_temperature"]["value"] - u["min_approach"]["value"] >= streams[sid]["temperature"]["value"], q
    # the reboiler takes MP steam: LP steam would leave about 6 K for the bubble point's
    # non-ideality and salt effect, MP steam about 38 K (D-008)
    assert energy["Q10"]["from"] == "MPS.c301"
    mps = utilities["MPS"]
    assert mps["supply_temperature"]["value"] - mps["min_approach"]["value"] - streams["S31"]["temperature"]["value"] > 30


def test_the_model_duties_are_cores(streams):
    for q in ("Q1", "Q2", "Q5", "Q9"):
        assert streams[q]["duty"]["provenance"] == "calculated"
        assert streams[q]["duty"]["source"].startswith("cheme process propagate: conversion duty")


def test_every_heat_stream_reaches_the_lci(streams):
    rows = {r["key"]: r for r in csv.DictReader((PROCESS / "lca" / "inventory.csv").open(encoding="utf-8"))}
    steam = rows["feed:LPS"]["streams"].split()
    mp = rows["feed:MPS"]["streams"].split()
    cw = rows["product:CW"]["streams"].split()
    assert sorted(steam) == sorted(["Q1", "Q3", "Q5", "Q6"])
    assert mp == ["Q10"]
    assert sorted(cw) == sorted(["Q2", "Q4", "Q7", "Q8", "Q9", "Q11", "Q12"])
    assert float(rows["feed:LPS"]["plant"]) == pytest.approx(sum(_duty(streams, q) for q in steam), abs=0.01)
    assert float(rows["feed:MPS"]["plant"]) == pytest.approx(_duty(streams, "Q10"), abs=0.01)


def test_the_oil_carbon_is_biogenic():
    content = _load("lca/lca.yaml")["carbon_accounting"]["content"]
    assert content["feed:OIL"]["biogenic_fraction"] == 1.0
    assert content["feed:MEOHF"]["biogenic_fraction"] == 0.0
    manifest = json.loads((PROCESS / "lca" / "manifest.json").read_text(encoding="utf-8"))
    carbon_in = manifest["balance"]["carbon"]["inputs"]
    # the oil's chains carry about 95 % of the carbon in (D-011)
    assert carbon_in["biogenic"] / (carbon_in["biogenic"] + carbon_in["fossil"]) == pytest.approx(0.948, abs=0.002)


def test_every_vessel_with_methanol_has_an_emission_exclusion(sheet, kg):
    """Derived from the flowsheet: every vessel, reactor or column whose step takes in methanol,
    and the flash with its vacuum pump, is named in an emission exclusion."""
    excluded = {tag for e in _load("lca/lca.yaml")["emission_exclusions"] for tag in e["equipment"]}
    types = {e["tag"]: e["type"] for e in _load("equipment/equipment-list.yaml")["equipment"]}
    holders = set()
    for step in sheet["steps"]:
        tags = [link["ref"] for link in step.get("links", []) if link["target"] == "equipment"]
        inlets = [s["id"] for s in sheet["streams"] if s.get("kind") != "energy" and s["to"].split(".")[0] == step["id"]]
        if tags and any(kg(sid).get("MEOH", 0.0) > 0 for sid in inlets):
            holders.update(t for t in tags if types[t] != "HeatExchanger" or t == "E-201")
    assert {"V-102", "V-103", "V-203", "C-303", "V-301"} <= holders
    assert holders <= excluded, sorted(holders - excluded)


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
