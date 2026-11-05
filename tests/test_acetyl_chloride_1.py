"""acetyl-chloride-1 (#142): the folder's stated numbers against its own flowsheet.

Fast, without core: the flowsheet's streams (propagated by core and given by
scripts/balance.py) are read as YAML, and the statements the folder makes in DESIGN.md,
README.md and process.yaml are checked against them:

- the yield on acetic acid and PCl3 (92.40 % of theory) and the specific PCl3 use (0.630 kg/kg)
  follow from S1, S3 and S10;
- the one-stage distillate S8 is the 97.3 wt% DESIGN.md states, and the product S10 the
  99.84 wt% with about 366 ppm P;
- the specified splits D101 and K101 close on their inlets, and the lower phase is close to the
  source it is calibrated to (CS 272 248 B2, Example 1, HCl-free);
- R101's vent fraction of acetyl chloride is the one scripts/balance.py estimates;
- the jacket's heating medium stays below the MTT, the still's below the decomposition of
  phosphorous acid, and the cooling check uses the log-mean water temperature;
- the criticality classes D-011 states as possible without a TD24 are the ones core's
  `criticality()` can give; the water and HCl release cases stay among the open items;
- the process is not set public in the change that adds it (CONTRIBUTING).
"""

from __future__ import annotations

import importlib.util
import math
import re
from pathlib import Path

import pytest
import yaml

KIT = Path(__file__).resolve().parents[1]
PROCESS = KIT / "processes" / "acetyl-chloride-1"
MW = {"ACOH": 60.052, "PCL3": 137.324, "ACCL": 78.495, "H3PO3": 81.995, "H2O": 18.015, "HCL": 36.458}


def _load(rel: str) -> dict:
    return yaml.safe_load((PROCESS / rel).read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def sheet() -> dict:
    return _load("process/flowsheet.yaml")


@pytest.fixture(scope="module")
def streams(sheet) -> dict[str, dict]:
    return {s["id"]: s["state"]["design"] for s in sheet["streams"]}


def _components(state: dict) -> dict[str, float]:
    """kg/h of each component (flow kg/h; mole or mass fractions)."""
    comp, flow = state["composition"], state["flow"]["value"]
    if comp["basis"] == "mass_fraction":
        return {n: flow * x for n, x in comp["values"].items()}
    mean = sum(x * MW[n] for n, x in comp["values"].items())
    return {n: flow * x * MW[n] / mean for n, x in comp["values"].items()}


def _text(rel: str) -> str:
    return " ".join((PROCESS / rel).read_text(encoding="utf-8").split())


def test_the_stated_yield_and_pcl3_use_follow_from_the_flowsheet(streams):
    acid = _components(streams["S1"])["ACOH"] / MW["ACOH"]
    pcl3 = _components(streams["S3"])["PCL3"] / MW["PCL3"]
    assert acid / pcl3 == pytest.approx(3.0, rel=1e-5)  # CS 272 248 B2, Example 1
    product = _components(streams["S10"])["ACCL"] / MW["ACCL"]
    assert product / acid == pytest.approx(0.9240, abs=5e-5)
    assert "92.40 % of theory" in _text("DESIGN.md")
    assert "92.4 % of theory" in _text("README.md") and "92.4 % of theory" in _text("process.yaml")
    specific = streams["S3"]["flow"]["value"] / streams["S10"]["flow"]["value"]
    assert specific == pytest.approx(0.630, abs=5e-4)


def test_one_still_stage_is_not_the_product_and_the_column_gives_the_stated_purity(streams):
    s8 = _components(streams["S8"])
    assert s8["ACCL"] / sum(s8.values()) == pytest.approx(0.9731, abs=1e-4)
    assert s8["PCL3"] / sum(s8.values()) == pytest.approx(0.0261, abs=1e-4)
    assert "97.31 wt% acetyl chloride with 2.61 wt% PCl3" in _text("DESIGN.md")
    s10 = _components(streams["S10"])
    assert s10["ACCL"] / sum(s10.values()) == pytest.approx(0.9984, abs=5e-5)
    ppm_p = s10["PCL3"] / sum(s10.values()) * 30.974 / MW["PCL3"] * 1e6
    assert ppm_p == pytest.approx(366, abs=1)


@pytest.mark.parametrize(("inlet", "outlets"), [("S4", ("S6", "S7")), ("S8", ("S10", "S11"))])
def test_the_specified_splits_close_on_their_inlets(streams, inlet, outlets):
    feed = _components(streams[inlet])
    out = {n: sum(_components(streams[o]).get(n, 0.0) for o in outlets) for n in feed}
    for name, value in feed.items():
        assert out[name] == pytest.approx(value, rel=1e-3, abs=1e-4), name


def test_the_lower_phase_is_close_to_the_source_it_is_calibrated_to(streams):
    s7 = _components(streams["S7"])
    total = sum(s7.values())
    # CS 272 248 B2, Example 1: 96 g with about 6 % HCl, 2 % AcCl, 10 % AcOH, the rest H3PO3;
    # the model vents its HCl, so the comparison is HCl-free
    source = {"H3PO3": 82 / 94, "ACOH": 10 / 94, "ACCL": 2 / 94}
    for name, share in source.items():
        assert s7[name] / total == pytest.approx(share, abs=0.01), name
    per_mol = total / (_components(streams["S3"])["PCL3"] / MW["PCL3"])  # g per mol PCl3
    assert per_mol == pytest.approx(96 * 0.94, rel=0.03)


def test_the_vent_fraction_is_the_scripts_estimate(sheet, streams):
    spec = importlib.util.spec_from_file_location("accl_balance", PROCESS / "scripts" / "balance.py")
    balance = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(balance)
    recipe = _load("process/recipe.yaml")
    hours = recipe["hours_per_year"]["value"]
    batches = balance.CAPACITY * hours / recipe["batch_size"]["value"]
    inert = _components(streams["S5"])["HCL"] / MW["HCL"] + balance.N2_VENT_NM3_PER_BATCH / 22.414 * batches / hours
    p_cold = balance.psat("ACCL", balance.T_VENT)
    passing = inert * p_cold / (balance.P - p_cold)
    s1, s3 = _components(streams["S1"]), _components(streams["S3"])
    pcl3 = s3["PCL3"] / MW["PCL3"]
    converted = pcl3 - _components(streams["S4"])["PCL3"] / MW["PCL3"]
    formed = 3.0 * (converted - s1["H2O"] / MW["H2O"] / 3.0)
    step = next(s for s in sheet["steps"] if s["id"] == "R101")
    stated = step["batch"]["vent"]["fraction"]["ACCL"]
    assert stated == pytest.approx(passing / formed, rel=0.01)
    assert f"{stated * 100:.3f} %" in _text("DESIGN.md")


def test_heating_media_stay_below_the_stated_limits_and_the_jacket_uses_the_log_mean(sheet):
    step = next(s for s in sheet["steps"] if s["id"] == "R101")
    mtt = step["hazard"]["mtt"]
    jacket = _load("process/recipe.yaml")["unit_procedures"][0]["vessel"]["jacket"]
    assert jacket["heating_temperature"] < mtt - 2.0  # the tempered water warms the acid below the MTT
    lmtd = (15.0 - 5.0) / math.log(15.0 / 5.0)  # cooling water 298.15 -> 308.15 K against 313.15 K
    assert jacket["coolant_temperature"] == pytest.approx(313.15 - lmtd, abs=0.01)
    lps = next(f for f in sheet["feeds"] if f["id"] == "LPS")
    assert lps["utility"]["supply_temperature"]["value"] < 473.0  # H3PO3 disproportionates at about 200 C


def test_the_mixed_residue_temperature_follows_from_its_inlets(streams):
    t9, t11, t12 = (streams[s]["temperature"]["value"] for s in ("S9", "S11", "S12"))
    assert min(t9, t11) - 0.01 <= t12 <= max(t9, t11) + 0.01


def test_not_published_in_the_change_that_adds_it():
    manifest = _load("process.yaml")
    assert manifest["publication"]["status"] == "internal"
    assert "license" not in manifest["publication"]


def _criticality(mtsr: float, mtt: float, td24: float) -> int:
    """Stoessel's class as core v1.8.0's reaction_hazards.criticality gives it."""
    if td24 < mtsr:
        return 4 if mtt < td24 else 5
    if mtsr < mtt:
        return 1 if mtt < td24 else 2
    return 3


def test_the_stated_criticality_classes_are_those_any_td24_can_give():
    rows = re.findall(
        r"^\| (?:5\.5e-4 \(design\)|k/10|k/100) \| [^|]+ \| ([\d.]+) K \| [^|]+ \| [^|]+ \| [^|]+ \| ([^|]+) \|$",
        (PROCESS / "DESIGN.md").read_text(encoding="utf-8"),
        flags=re.M,
    )
    assert len(rows) == 3
    mtt = 324.15
    for mtsr, stated in rows:
        possible = {_criticality(float(mtsr), mtt, 290.0 + 0.25 * i) for i in range(400)}
        assert {int(c) for c in re.findall(r"\d", stated)} == possible, (mtsr, stated)
    assert "and 5 if it lies below (TD24 < 315.8 K)" in _text("DESIGN.md")


def test_water_ingress_and_the_sources_hcl_are_open_items(streams):
    # 1 kg of water with PCl3 or acetyl chloride: one HCl per water, as gas at 313 K, 101.325 kPa
    volume = 1.0 / MW["H2O"] * 8.314 * 313.15 / 101.325
    assert volume == pytest.approx(1.43, abs=0.005)
    design = _text("DESIGN.md")
    assert "about 1.43 m3 at 313 K" in design
    assert "Loss of the scrubber water while R-101 doses" in design
    # CS 272 248 B2: 6 wt% HCl in 96 g of lower phase per mol PCl3, at this plant's batch
    cycle = _load("process/recipe.yaml")["batch_size"]["value"] / streams["S10"]["flow"]["value"]
    pcl3 = streams["S3"]["flow"]["value"] * cycle / MW["PCL3"]
    assert pcl3 * 0.06 * 96 == pytest.approx(38.6, abs=0.1)
    assert "38.6 kg a batch" in design
    equipment = _text("equipment/equipment-list.yaml")
    assert "anti-suck-back" in equipment and "scrubber's water flow" in equipment


def test_the_allocation_shares_are_the_mass_shares_of_the_coproducts(streams):
    allocation = _load("lca/lca.yaml")["allocation"]
    product, crude = streams["S10"]["flow"]["value"], streams["S7"]["flow"]["value"]
    assert allocation["shares"]["ACCL"] == pytest.approx(product / (product + crude), abs=5e-4)
    assert sum(allocation["shares"].values()) == pytest.approx(1.0)


def test_the_scrubber_bleed_is_one_percent_hcl(streams):
    bleed = _components(streams["S16"])
    assert bleed["HCL"] / sum(bleed.values()) == pytest.approx(0.01, abs=1e-4)
