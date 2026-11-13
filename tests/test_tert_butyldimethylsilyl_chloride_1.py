"""tert-butyldimethylsilyl-chloride-1 (#147): the folder's stated numbers against its own files.

Fast, mostly without core: the statements the folder makes in DESIGN.md, the equipment list and
the stream sources are recomputed from the values its YAML files hold (the lessons of the
library's earlier batch reviews):

- the LCA dataset and manifest name the hashes of the input files as they are committed;
- the batch basis: the recipe's batch over the product's year-average flow is the cycle D-003
  states, and the capacity and yield of D-002 follow from the streams (the yield below the
  patent's 78 %);
- the jackets take the brine at its log-mean driving force against each vessel's content, and
  R-101's warm-up medium lies below the screening's MTT (tert-butyl chloride's boiling point);
- the mixed streams' temperatures follow from their inlets, and the hand duties Q7, Q9 and Q10
  from the stream table;
- the hydrogen of the salt's quench, the HCl and isobutane of water ingress, the halide a cooling
  failure drives out and the per-batch consumables follow from the streams and the cycle;
- R-101's vent capacity against D-011's gas release: within it at the base rate, exceeded at
  k/10 and k/100 (the design finding); with core importable, the screening's own MTSR, MTT and
  gas release are D-011's.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
from pathlib import Path

import pytest
import yaml

KIT = Path(__file__).resolve().parents[1]
PROCESS = KIT / "processes" / "tert-butyldimethylsilyl-chloride-1"

#: m3(STP)/kmol at 273.15 K and 101.325 kPa
NM3_PER_KMOL = 22.414
#: kg/Nm3 of nitrogen
N2_DENSITY = 1.2506
#: kg/kmol of sodium thiocyanate (IUPAC 2021 atomic weights)
NASCN = 81.07


def _yaml(rel: str):
    return yaml.safe_load((PROCESS / rel).read_text(encoding="utf-8"))


def _section(decision: str) -> str:
    """One DESIGN.md decision, whitespace collapsed."""
    text = (PROCESS / "DESIGN.md").read_text(encoding="utf-8")
    m = re.search(rf"^## {decision} .*?(?=^## )", text, flags=re.S | re.M)
    assert m, f"DESIGN.md has no {decision}"
    return " ".join(m.group(0).split())


def _sha256(rel: str) -> str:
    return "sha256:" + hashlib.sha256((PROCESS / rel).read_bytes()).hexdigest()


@pytest.fixture(scope="module")
def model():
    materials = _yaml("process/materials.yaml")
    flowsheet = _yaml("process/flowsheet.yaml")
    recipe = _yaml("process/recipe.yaml")
    comps = {c["id"]: c for c in materials["components"]}
    streams = {s["id"]: s for s in flowsheet["streams"]}
    steps = {s["id"]: s for s in flowsheet["steps"]}
    procedures = {u["id"]: u for u in recipe["unit_procedures"]}
    batch = recipe["batch_size"]["value"]
    product = streams[recipe["batch_size"]["stream"]]["state"]["design"]["flow"]["value"]
    return {"comps": comps, "streams": streams, "steps": steps, "recipe": recipe,
            "procedures": procedures, "batch_hours": batch / product, "flowsheet": flowsheet}


def _state(model, sid: str) -> dict:
    return model["streams"][sid]["state"]["design"]


def _kmol(model, sid: str) -> dict[str, float]:
    """kmol/h of each component of a stream."""
    st = _state(model, sid)
    flow, comp = st["flow"]["value"], st["composition"]
    mm = {c: model["comps"][c]["molar_mass"] for c in comp["values"]}
    if comp["basis"] == "mole_fraction":
        mbar = sum(v * mm[c] for c, v in comp["values"].items())
        return {c: flow / mbar * v for c, v in comp["values"].items()}
    return {c: flow * v / mm[c] for c, v in comp["values"].items()}


def _cp_flow(model, sid: str) -> float:
    """kJ/(h K) of a stream from the declared liquid heat capacities."""
    return sum(n * model["comps"][c]["liquid_heat_capacity"] for c, n in _kmol(model, sid).items())


def _duty(model, sid: str) -> float:
    return _state(model, sid)["duty"]["value"]


def _number(pattern: str, text: str) -> float:
    m = re.search(pattern, text)
    assert m, pattern
    return float(m.group(1))


def test_lca_dataset_and_manifest_name_the_committed_inputs():
    """`cheme assess lca --check` fails when an input changed after the last --write."""
    dataset = _yaml("lca/dataset.yaml")
    manifest = json.loads((PROCESS / "lca" / "manifest.json").read_text(encoding="utf-8"))
    recorded = {**dataset["provenance"]["files"], **manifest["inputs"]}
    assert "process.yaml" in recorded
    stale = {rel: h for rel, h in recorded.items() if _sha256(rel) != h}
    assert not stale, f"rerun cheme assess lca --write: stale input hashes {sorted(stale)}"


def test_published_with_cc_by():
    assert _yaml("process.yaml")["publication"] == {"status": "public", "license": "CC-BY-4.0"}


def test_batch_basis_cycle_capacity_and_yield(model):
    d003, d002 = _section("D-003"), _section("D-002")
    cycle = _number(r"R-101 is the bottleneck: cycle ([\d.]+) h", d003)
    batches = _number(r"cycle [\d.]+ h, ([\d.]+) batches in 7920 h", d003)
    assert abs(cycle - model["batch_hours"]) < 0.01, (cycle, model["batch_hours"])
    assert abs(batches - 7920 / model["batch_hours"]) < 1.0, batches
    product = _state(model, "S25")["flow"]["value"]
    tpa = _number(r"from the recipe \(D-003\): ([\d.]+) t/a", d002)
    assert abs(tpa - product * 7920 / 1000) < 0.1, tpa
    yield_ = _number(r"The yield is ([\d.]+) % on the tert-butyl chloride", d002)
    calc = _kmol(model, "S25")["TBSCL"] / _kmol(model, "S4")["TBUCL"] * 100
    assert abs(yield_ - calc) < 0.05, (yield_, calc)
    assert calc < 78.0, "a headline yield never above the source's 78 % (US 5 068 386 A)"
    # REACT's stated operations add up to the cycle
    times = [0.415, 3.25, 0.195]
    fixed = sum(op["duration"]["value"] for op in model["procedures"]["REACT"]["operations"]
                if "duration" in op)
    assert abs(fixed + sum(times) - cycle) < 0.01, fixed + sum(times)


def _log_mean_equivalent(content: float, supply: float, ret: float) -> float:
    hot, cold = content - supply, content - ret
    return content - (hot - cold) / math.log(hot / cold)


def test_jackets_at_the_log_mean_driving_force(model):
    brine = next(p for p in model["flowsheet"]["products"] if p["id"] == "BRINE")["utility"]
    supply, ret = brine["supply_temperature"]["value"], brine["return_temperature"]["value"]
    for proc, sid in (("REACT", "S6B"), ("SILYL", "S9")):
        content = _state(model, sid)["temperature"]["value"]
        jacket = model["procedures"][proc]["vessel"]["jacket"]
        expected = _log_mean_equivalent(content, supply, ret)
        assert abs(jacket["coolant_temperature"] - expected) < 0.02, (proc, jacket, expected)


def test_r101_heating_medium_below_the_mtt(model):
    jacket = model["procedures"]["REACT"]["vessel"]["jacket"]
    mtt = model["comps"]["TBUCL"]["normal_boiling_point"]
    assert jacket["heating_temperature"] < mtt, (jacket, mtt)
    assert "below the screening's MTT" in _section("D-010")


def test_condensers_above_the_freezing_points(model):
    """Brine above tert-butyl chloride's 247 K; the product cut's hot water above TBSCl's
    358.1 K (D-007)."""
    brine = next(p for p in model["flowsheet"]["products"] if p["id"] == "BRINE")["utility"]
    assert brine["supply_temperature"]["value"] > 247.0 + 10
    tw = next(p for p in model["flowsheet"]["products"] if p["id"] == "TW")["utility"]
    assert "368.15 K" in tw["supply_temperature"]["source"] and 368.15 > 358.1
    assert "10 K above TBSCl's melting point (358.1 K" in _section("D-007")


@pytest.mark.parametrize("mixer,inlets", [
    ("S6", {"S1": None, "S2": None, "S3": None, "S30": "S27"}),
    ("S33", {"S5": None, "S32": "S27"}),
    ("S12", {"S10": "S9", "S20": "S27"}),
    ("S21", {"S11": "S9", "S14": "S12"}),
])
def test_mixed_temperatures_from_their_inlets(model, mixer, inlets):
    """A splitter's or a filter's outlet carries its inlet's temperature (`via`)."""
    num = den = 0.0
    for sid, via in inlets.items():
        t = _state(model, via or sid)["temperature"]["value"]
        cp = _cp_flow(model, sid)
        num, den = num + cp * t, den + cp
    assert abs(_state(model, mixer)["temperature"]["value"] - num / den) < 0.1, (mixer, num / den)


def test_recycle_mix_and_cooler_q10(model):
    num = _cp_flow(model, "S22") * _state(model, "S22")["temperature"]["value"]
    num += _cp_flow(model, "S19") * _state(model, "S17")["temperature"]["value"]
    t_mix = num / (_cp_flow(model, "S22") + _cp_flow(model, "S19"))
    assert abs(_state(model, "S26")["temperature"]["value"] - t_mix) < 0.1, t_mix
    q10 = _cp_flow(model, "S26") * (t_mix - _state(model, "S27")["temperature"]["value"]) / 3600
    assert abs(_duty(model, "Q10") - q10) < 0.02 * q10, (q10, _duty(model, "Q10"))


def test_flaker_q7(model):
    tbscl = model["comps"]["TBSCL"]
    n = _kmol(model, "S23")["TBSCL"]
    per_kmol = tbscl["liquid_heat_capacity"] * (398.15 - 308.15) + 5600.0
    assert abs(_duty(model, "Q7") - n * per_kmol / 3600) < 0.03, n * per_kmol / 3600


def test_dryer_condenser_q9_with_the_vacuum_pump(model):
    latent = {"THF": 30600, "HEX": 30200, "TBUCL": 25500, "ME2SICL2": 29600, "TBSCL": 37100}
    vap = _kmol(model, "S16")
    q = sum(n * latent[c] for c, n in vap.items()) + _cp_flow(model, "S16") * (343.15 - 268.15)
    pump = 2.0 * 5.51 / 9.86
    assert abs(_duty(model, "Q9") - (q / 3600 + pump)) < 0.05, (q / 3600, pump)


def test_quench_hydrogen_and_water_ingress(model):
    hours = model["batch_hours"]
    d006, d011 = _section("D-006"), _section("D-011")
    mg = _kmol(model, "S15")["MG"] * hours
    assert abs(_number(r"is about ([\d.]+) kmol, [\d.]+ kg or \d+ Nm3 of hydrogen", d006) - mg) < 0.005
    assert abs(_number(r"kmol, [\d.]+ kg or (\d+) Nm3 of hydrogen", d006) - mg * NM3_PER_KMOL) < 1.0
    sil = _kmol(model, "S33")["ME2SICL2"] * hours
    assert abs(_number(r"charge holds ([\d.]+) kmol of silane a batch", d011) - sil) < 0.01
    hcl = _number(r"up to about [\d.]+ kmol \((\d+) Nm3\) of HCl", d011)
    assert abs(hcl - 2 * sil * NM3_PER_KMOL) < 1.0, hcl
    grig = _kmol(model, "S7")["TBUMGCL"] * hours
    assert abs(_number(r"Grignard solution ([\d.]+) kmol of reagent", d011) - grig) < 0.01


def test_accumulated_halide_amounts(model):
    d011 = _section("D-011")
    dosed = _state(model, "S4")["flow"]["value"] * model["batch_hours"]
    assert abs(_number(r"the ([\d.]+) kg dosed per batch", d011) - dosed) < 0.1
    for label, acc in (("at the base rate", 0.0221), ("at k/10", 0.155), ("at k/100", 0.629)):
        stated = _number(rf"about (\d+) kg {re.escape(label)}", d011)
        assert abs(stated - acc * dosed) <= 1.0, (label, stated, acc * dosed)
    assert abs(_number(r"about (\d+) kg for an uninitiated 5 %", d011) - 0.999 * 0.05 * dosed) <= 1.0


def test_per_batch_consumables(model):
    lca = _yaml("lca/lca.yaml")
    cons = {c["id"]: c for c in lca["consumables"]}
    halide = _kmol(model, "S4")["TBUCL"] * model["batch_hours"]
    assert abs(cons["sodium-thiocyanate"]["per_batch"] - 0.008 * halide * NASCN) < 0.01
    nm3 = _number(r"([\d.]+) Nm3 per batch", cons["nitrogen"]["source"])
    assert abs(cons["nitrogen"]["per_batch"] - nm3 * N2_DENSITY) < 0.1
    parts = [float(x) for x in re.findall(r"\(([\d.]+)\)", cons["nitrogen"]["source"].split("ASSUMED")[1])]
    assert abs(sum(parts) + 18.9 - nm3) < 0.05, parts
    assert abs(19.7 - 2 * 9.86) < 0.05


def test_per_kg_statements(model):
    d012 = _section("D-012")
    product = _state(model, "S25")["flow"]["value"]
    for name, sid in (("magnesium", "S1"), ("tert-butyl chloride", "S4"), ("dichlorodimethylsilane", "S5")):
        stated = _number(rf"Per kg of TBSCl: .*?{re.escape(name)} ([\d.]+) kg", d012)
        assert abs(stated - _state(model, sid)["flow"]["value"] / product) < 0.001, name
    brine = sum(_duty(model, q) for q in ("Q1", "Q2", "Q3", "Q9")) / product
    assert abs(_number(r"brine ([\d.]+) kWh removed", d012) - brine) < 0.006, brine
    mps = _duty(model, "Q5") / product
    assert abs(_number(r"MP steam ([\d.]+) kWh", d012) - mps) < 0.006, mps


def _d011_gas() -> dict[str, float]:
    d011 = _section("D-011")
    gas = {}
    for name, key in (("base (ASSUMED k)", "base"), ("k/10", "k/10"),
                      ("k/100 (sluggish or delayed initiation)", "k/100")):
        m = re.search(rf"\| {re.escape(name)} \|(?:[^|]*\|){{2}} ([\d.]+) m3/h \|", d011)
        assert m, f"D-011: no gas release for {name}"
        gas[key] = float(m.group(1))
    return gas


def test_vent_capacity_against_the_gas_release(model):
    hazard = model["steps"]["R101"]["hazard"]
    capacity = hazard["vent_capacity"]
    assert hazard["provenance"] == "assumed" and "ASSUMED" in hazard["source"]
    gas = _d011_gas()
    assert gas["base"] < capacity < gas["k/10"] < gas["k/100"], gas
    d011 = _section("D-011")
    assert "Design finding, the vent" in d011
    assert f"{gas['k/10'] / capacity:.1f} times the 100 m3/h" in d011
    assert f"{gas['k/100'] / capacity:.1f} times" in d011


def test_screening_reproduces_d011(model):
    """With core importable: the screening's own MTSR, MTT and gas release are D-011's."""
    rh = pytest.importorskip("chemeascode.domains.safety.reaction_hazards")
    report = rh.screen(PROCESS)
    r101 = next(e for e in report.entries if e.node == "R101")
    r102 = next(e for e in report.entries if e.node == "R102")
    assert abs(r101.mtt - model["comps"]["TBUCL"]["normal_boiling_point"]) < 0.05, r101.mtt
    assert abs(r101.mtsr - 317.7) < 0.05 and abs(r102.mtsr - 309.3) < 0.05
    release = r101.gas_release
    assert release and release["vent_capacity_m3_h"] == 100.0
    assert abs(release["rate_m3_h"] - _d011_gas()["base"]) < 0.05, release["rate_m3_h"]
