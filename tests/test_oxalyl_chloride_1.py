"""oxalyl-chloride-1 (#144): the folder's stated numbers against its own flowsheet.

Fast, without core where it can be: the flowsheet's streams (propagated by core and given by
scripts/balance.py) are read as YAML, and the statements the folder makes in DESIGN.md,
README.md and process.yaml are checked against them:

- the yield on the oxalic acid (77.2 % of theory), the vented share (7.4 %) and the specific
  consumptions follow from S8, S12, S17 and the feeds, and stay below the source's isolated
  84.2 % (US 4 341 720 A, Examples 19 and 20: 445 g from 375 g of acid);
- the feed ratios are the script's, the product cut is 99.50 wt% with the stated impurities;
- the specified split D101 closes on its inlet per component;
- the mixed charges' temperatures follow from their inlets, the stills' streams are at their
  bubble points, and the MTTs are the bubble points the script gives;
- every heating medium stays below the MTTs, the cooling check uses the log-mean water
  temperature, and the chilled water stays above POCl3's melting point;
- the criticality classes DESIGN.md states as possible without a TD24 are the ones core's
  `criticality()` can give; the k/100 release above the vent is a recorded design finding;
- the allocation shares are the products' values at the stated relative prices;
- every heat stream reaches the LCI, and every vent source has an emission exclusion;
- with core: the screening's MTSRs and the gas release against the vent, the recipe's basis,
  vessel and R102's jacket, and R101's jacket checked by hand with core's `wetted_area`;
- the process is public with CC-BY-4.0 and requires cheme-as-code 1.11.
"""

from __future__ import annotations

import csv
import importlib.util
import re
from pathlib import Path

import pytest
import yaml

KIT = Path(__file__).resolve().parents[1]
PROCESS = KIT / "processes" / "oxalyl-chloride-1"


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


@pytest.fixture(scope="module")
def balance():
    spec = importlib.util.spec_from_file_location("oxcl_balance", PROCESS / "scripts" / "balance.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _step(sheet: dict, sid: str) -> dict:
    return next(s for s in sheet["steps"] if s["id"] == sid)


def _kg(balance, streams, sid: str) -> dict[str, float]:
    return {n: v for n, v in balance.component_flows({sid: {"state": {"design": streams[sid]}}}, sid).items()}


def test_the_stated_yield_and_consumptions_follow_from_the_flowsheet(balance, streams):
    acid = _kg(balance, streams, "S8")["OXA"] / balance.MW["OXA"]
    product = _kg(balance, streams, "S17")
    total = sum(product.values())
    yield_ = product["OXCL"] / balance.MW["OXCL"] / acid
    vented = _kg(balance, streams, "S12")["OXCL"] / balance.MW["OXCL"] / acid
    assert yield_ == pytest.approx(0.7716, abs=5e-5)
    assert vented == pytest.approx(0.0741, abs=5e-5)
    # the source: 445 g isolated from 375 g of acid; the crude 2052 g at 21.9 wt%
    isolated = 445.0 / balance.MW["OXCL"] / (375.0 / balance.MW["OXA"])
    crude = 2052.0 * 0.219 / balance.MW["OXCL"] / (375.0 / balance.MW["OXA"])
    assert isolated == pytest.approx(0.842, abs=5e-4) and crude == pytest.approx(0.850, abs=5e-4)
    assert yield_ < isolated
    assert "77.2 % of theory on the oxalic acid" in _text("README.md")
    assert "product S17 holds 77.16 % of theory on the oxalic acid" in _text("DESIGN.md")
    assert "7.41 % of the acid's worth passes E-102" in _text("DESIGN.md")
    for sid, stated in {"S1": 2.672, "S6": 1.386, "S8": 0.915, "S21": 1.951, "S20": 2.683, "S23": 2.792, "S15": 0.285}.items():
        assert streams[sid]["flow"]["value"] / total == pytest.approx(stated, abs=5e-4), sid
    assert "PCl3 2.672 kg" in _text("DESIGN.md") and "2.672 kg/kg oxalyl chloride" in _text("process.yaml")
    # the crude's assay against the source's 21.9 wt%
    crude13 = _kg(balance, streams, "S13")
    assert crude13["OXCL"] / sum(crude13.values()) == pytest.approx(0.204, abs=5e-4)


def test_the_product_cut_and_the_feed_ratios(balance, streams):
    product = _kg(balance, streams, "S17")
    total = sum(product.values())
    assert product["OXCL"] / total == pytest.approx(0.9950, abs=5e-5)
    assert product["POCL3"] / total == pytest.approx(0.0044, abs=5e-5)
    assert product["PCL3"] / total == pytest.approx(0.0006, abs=5e-5)
    assert "99.50 wt% with 0.44 wt% POCl3 and 0.06 wt% PCl3" in _text("process/design-basis.yaml")
    n = {sid: _kg(balance, streams, sid) for sid in ("S1", "S6", "S8", "S2")}
    pcl3 = n["S1"]["PCL3"] / balance.MW["PCL3"]
    assert pcl3 / (n["S8"]["OXA"] / balance.MW["OXA"]) == pytest.approx(balance.PCL3_PER_ACID, rel=1e-4)
    assert n["S6"]["CL2"] / balance.MW["CL2"] / pcl3 == pytest.approx(balance.CL2_PER_PCL3, rel=1e-4)
    assert n["S2"]["LUT"] / n["S1"]["PCL3"] == pytest.approx(balance.LUT_PER_PCL3, rel=1e-3)
    assert streams["S17"]["flow"]["value"] == pytest.approx(balance.CAPACITY, rel=1e-4)


def test_the_specified_split_closes_on_its_inlet(balance, streams):
    inlet = _kg(balance, streams, "S22")
    out = {}
    for sid in ("S23", "S24"):
        for n, v in _kg(balance, streams, sid).items():
            out[n] = out.get(n, 0.0) + v
    for n in set(inlet) | set(out):
        assert out.get(n, 0.0) == pytest.approx(inlet.get(n, 0.0), abs=2e-3), n
    acid = _kg(balance, streams, "S23")
    assert acid["HCL"] / sum(acid.values()) == pytest.approx(balance.HCL_ACID, abs=1e-6)


def test_mixed_and_bubble_point_temperatures(balance, streams):
    kg = lambda sid: _kg(balance, streams, sid)  # noqa: E731
    t14 = balance.bubble_point(balance.kmol(kg("S14")), balance.P_STRIP, solids=True)
    assert streams["S14"]["temperature"]["value"] == pytest.approx(t14, abs=0.01)
    t4 = balance.mixed_temperature([(kg("S1"), 298.15), (kg("S2"), 298.15), (kg("S3"), t14)])
    assert streams["S4"]["temperature"]["value"] == pytest.approx(t4, abs=0.01)
    t25 = balance.bubble_point(balance.kmol(kg("S25")), balance.P_ATM)
    t10 = balance.mixed_temperature([(kg("S8"), 298.15), (kg("S9"), 303.15), (kg("S25"), t25)])
    assert streams["S10"]["temperature"]["value"] == pytest.approx(t10, abs=0.01)
    for sid, pressure in {"S13": balance.P_STRIP, "S16": balance.P_ATM, "S18": balance.P_ATM}.items():
        t = balance.bubble_point(balance.kmol(kg(sid)), pressure)
        assert streams[sid]["temperature"]["value"] == pytest.approx(t, abs=0.01), sid
    assert _step({"steps": _load("process/flowsheet.yaml")["steps"]}, "ST101")["still"]["pressure"] == balance.P_STRIP


def test_the_mtts_are_the_bubble_points_of_the_vented_mass(balance, sheet, streams):
    for step, sid in {"R101": "S5", "R102": "S11"}.items():
        stated = _step(sheet, step)["hazard"]["mtt"]
        t = balance.bubble_point(balance.kmol(_kg(balance, streams, sid)), balance.P_ATM)
        assert stated == pytest.approx(t, abs=0.01), step


def test_heating_and_cooling_media_against_the_stated_limits(sheet):
    mtts = [_step(sheet, s)["hazard"]["mtt"] for s in ("R101", "R102")]
    jacket = _load("process/recipe.yaml")["unit_procedures"][0]["vessel"]["jacket"]
    # the hot-water loop at 353/348 K: its supply below both MTTs
    assert jacket["heating_temperature"] == pytest.approx((353.15 + 348.15) / 2)
    assert 353.15 < min(mtts)
    # cooling water 298/308 K against the mass at 333.15 K: the log-mean driving force
    import math

    lmtd = (35.0 - 25.0) / math.log(35.0 / 25.0)
    assert jacket["coolant_temperature"] == pytest.approx(333.15 - lmtd, abs=0.005)
    # chilled water above POCl3's melting point (CRC via chemicals 1.5.2), which condenses on E-102
    chw = next(p for p in sheet["products"] if p["id"] == "CHW")["utility"]["supply_temperature"]["value"]
    assert chw > 274.33
    vent = _step(sheet, "R102")["batch"]["vent"]["condenser"]
    assert vent["temperature"] == pytest.approx(chw + 5.0)
    # the strip's end, where the still is hottest, below the loop's mean (D-007)
    s14 = next(s for s in sheet["streams"] if s["id"] == "S14")["state"]["design"]["temperature"]["value"]
    assert s14 < jacket["heating_temperature"]


def _criticality(mtsr: float, mtt: float, td24: float) -> int:
    """Stoessel's class as core's reaction_hazards.criticality gives it."""
    if td24 < mtsr:
        return 4 if mtt < td24 else 5
    if mtsr < mtt:
        return 1 if mtt < td24 else 2
    return 3


def test_the_stated_criticality_classes_are_those_any_td24_can_give(sheet):
    rows = re.findall(
        r"^\| (design|k/10|k/100) \| ([\d.]+) %, ([\d.]+) K \| ([\d.]+) %, ([\d.]+) K \| [^|]+ \| ([\d.]+) \| [^|]+ \| [^|]+ \| ([^|]+) \|$",
        (PROCESS / "DESIGN.md").read_text(encoding="utf-8"),
        flags=re.M,
    )
    assert [r[0] for r in rows] == ["design", "k/10", "k/100"]
    mtt101, mtt102 = (_step(sheet, s)["hazard"]["mtt"] for s in ("R101", "R102"))
    for case, _a1, mtsr101, _a2, mtsr102, ratio, stated in rows:
        possible = set()
        for mtsr, mtt in ((float(mtsr101), mtt101), (float(mtsr102), mtt102)):
            possible |= {_criticality(mtsr, mtt, 300.0 + 0.25 * i) for i in range(400)}
        assert {int(c) for c in re.findall(r"\d", stated)} == possible, case
    # the design finding: k/100 above the vent's capacity
    k100 = next(r for r in rows if r[0] == "k/100")
    assert float(k100[5]) > 1.0
    assert "Design finding (k/100" in _text("DESIGN.md")


def test_the_allocation_shares_are_the_values_at_the_stated_prices(streams):
    study = _load("lca/lca.yaml")
    prices = {"OXCLP": 1.0, "POCL3P": 0.25, "HCLAQ": 0.02}
    flows = {"OXCLP": "S17", "POCL3P": "S20", "HCLAQ": "S23"}
    values = {k: streams[sid]["flow"]["value"] * prices[k] for k, sid in flows.items()}
    total = sum(values.values())
    shares = study["allocation"]["shares"]
    assert sum(shares.values()) == pytest.approx(1.0, abs=1e-9)
    for k, v in values.items():
        assert shares[k] == pytest.approx(v / total, abs=5e-4), k
    assert "1 : 0.25 : 0.02" in _text("lca/lca.yaml")
    mass = streams["S17"]["flow"]["value"] / sum(streams[sid]["flow"]["value"] for sid in flows.values())
    assert mass == pytest.approx(0.154, abs=5e-4)
    assert "15.4 %" in _text("DESIGN.md")


def test_every_heat_stream_reaches_the_lci(streams):
    with (PROCESS / "lca" / "inventory.csv").open(encoding="utf-8") as fh:
        rows = {r["key"]: r for r in csv.DictReader(fh)}
    duty = lambda *ids: sum(streams[i]["duty"]["value"] for i in ids)  # noqa: E731
    expected = {
        "feed:LPS": ("Q1", "Q5", "Q7"),
        "product:CW": ("Q2", "Q3", "Q8", "Q9", "Q10", "Q11"),
        "product:CHW": ("Q4", "Q6"),
        "feed:POWER": ("P1", "P2", "P3"),
    }
    product = streams["S17"]["flow"]["value"]
    stated = {"feed:LPS": 1.368, "product:CW": 2.017, "product:CHW": 0.447, "feed:POWER": 0.158}
    for key, ids in expected.items():
        assert float(rows[key]["plant"]) == pytest.approx(duty(*ids), abs=1e-3), key
        assert sorted(rows[key]["streams"].split()) == sorted(ids), key
        assert duty(*ids) / product == pytest.approx(stated[key], abs=5e-4), key
    # every energy stream of the flowsheet is in one of them
    counted = {i for ids in expected.values() for i in ids}
    energy = {sid for sid, s in streams.items() if "duty" in s}
    assert energy == counted


def test_every_vent_source_has_an_emission_exclusion():
    ids = {e["id"] for e in _load("lca/lca.yaml")["emission_exclusions"]}
    assert {"vent-nitrogen", "vacuum-pump", "storage-breathing"} <= ids


def test_the_release_cases_are_open_items():
    design = _text("DESIGN.md")
    for case in ("(a) Water ingress", "(b) Loss of the absorber's water", "(c) Chlorine", "(d) CO", "(e) Loss of chilled water", "(f) Failure of the hot-water loop"):
        assert case in design, case
    assert "must not pass activated carbon" in design


def test_published_public_with_cc_by():
    assert _load("process.yaml")["publication"] == {"status": "public", "license": "CC-BY-4.0"}


def test_requires_core_1_11():
    assert _load("plant.yaml")["requires"] == "cheme-as-code>=1.11"
    assert "Needs cheme-as-code 1.11.0" in _text("README.md") and "Needs cheme-as-code 1.11.0" in _text("process.yaml")
    assert "## Core features used (core 1.11.0)" in (PROCESS / "DESIGN.md").read_text(encoding="utf-8")


# ---- with core ----------------------------------------------------------------------------


def test_core_screens_both_semi_batches_and_the_vent():
    pytest.importorskip("chemeascode")
    from chemeascode.domains.safety.reaction_hazards import screen

    report = screen(PROCESS)
    r101 = next(e for e in report.entries if e.node == "R101")
    r102 = next(e for e in report.entries if e.node == "R102")
    assert r101.mtsr == pytest.approx(335.11, abs=0.01) and r101.accumulation == pytest.approx(0.0096, abs=5e-5)
    assert r102.mtsr == pytest.approx(333.98, abs=0.01) and r102.accumulation == pytest.approx(0.0293, abs=5e-5)
    gas = r102.gas_release
    assert gas["rate_m3_h"] == pytest.approx(282.8, abs=0.1)
    assert gas["vent_capacity_m3_h"] == 350.0 and gas["capacity_ratio"] == pytest.approx(0.81, abs=0.005)
    # the vent capacity is the release at the MTSR plus about 20 %, rounded up
    assert 1.15 < 350.0 / gas["rate_m3_h"] < 1.3
    assert not [f for f in report.findings if f.level in ("warning", "error")]
    design = _text("DESIGN.md")
    assert "MTSR 335.11 K" in design and "MTSR 333.98 K" in design and "282.8 m3/h" in design


def test_the_recipe_basis_vessel_and_jackets():
    pytest.importorskip("chemeascode")
    from chemeascode.domains.process.recipe import recipe_report, wetted_area

    result = recipe_report(PROCESS)
    assert not [f for f in result.findings if f.level in ("warning", "error")]
    vessel = next(v for v in result.vessels if v.procedure == "REACT")
    assert vessel.volume == 12.5 and vessel.removable > vessel.peak_duty
    # R101's jacket by hand (L-5): its peak per m3 at the end of the dosing, at R101's own charge
    from chemeascode.domains.process.model import load
    from chemeascode.domains.process.stirred_tank import solve_node

    process, _ = load(PROCESS)
    case = process.flowsheet.default_case()
    item = process.nodes["R101"]
    inlets = [s for s in process.flowsheet.streams if s.kind == "material" and (end := process.ends(s)[1]) is not None and end.node == "R101"]
    solved, _ = solve_node(process, item, inlets, case)
    st = {s["id"]: s["state"]["design"] for s in _load("process/flowsheet.yaml")["streams"] if "state" in s}
    hours = _load("process/recipe.yaml")["batch_size"]["value"] / st["S17"]["flow"]["value"]
    # the model's peak (kW/m3) on its end volume, the jacket at its charge (m3 per hour of flows)
    r101_peak = solved.peak_cooling_duty * solved.volume * hours
    jacket = _load("process/recipe.yaml")["unit_procedures"][0]["vessel"]["jacket"]
    area = wetted_area(solved.charge_volume * hours, vessel.diameter)
    removable = jacket["u"] / 1000.0 * area * (333.15 - jacket["coolant_temperature"])
    assert r101_peak == pytest.approx(105.6, abs=0.1) and removable == pytest.approx(133.1, abs=0.1)
    assert r101_peak / removable == pytest.approx(0.79, abs=0.005)
    design = _text("DESIGN.md")
    assert f"{solved.peak_cooling_duty:.2f} kW/m3 x {solved.volume * hours:.2f} m3 = 105.6 kW" in design
    assert f"{area:.2f} m2 (at R101's charge, {solved.charge_volume * hours:.2f} m3" in design
    assert "133.1 kW (0.79)" in design
    assert f"R102's peak {vessel.peak_duty:.1f} kW" in _text("equipment/equipment-list.yaml")
