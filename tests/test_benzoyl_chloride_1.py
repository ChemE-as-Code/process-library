"""benzoyl-chloride-1 (#156): the folder's stated numbers against its own flowsheet.

Fast, without core: the flowsheet's streams (propagated by core and given by
scripts/balance.py) are read as YAML, and the statements the folder makes in DESIGN.md and
process.yaml are checked against them:

- the yield on benzotrichloride (97.19 % of theory, two benzoyl chloride per benzotrichloride)
  and the specific benzotrichloride use (0.715 kg/kg) follow from S4 and S11;
- the product meets the patent's purity (above 99.5 %) and the absorber makes 30 wt% acid;
- the column's specified split K101 closes on the still's distillate S9;
- the process is not set public in the change that adds it (CONTRIBUTING, "Publishing a
  process");
- (review of #390) the criticality classes D-011 states as possible without a TD24 are the ones
  Stoessel's scheme (core's `criticality()`) can give for the stated MTSR and MTT; the residue
  S13 is drained above its ideal benzoic acid liquidus; and the water and HCl release cases
  stay among the open items with their stoichiometric gas volume.
"""

from __future__ import annotations

import math
import re
from pathlib import Path

import pytest
import yaml

KIT = Path(__file__).resolve().parents[1]
PROCESS = KIT / "processes" / "benzoyl-chloride-1"
MW = {"BTC": 195.467, "BA": 122.123, "BZCL": 140.566, "ZNCL2": 136.28, "HCL": 36.458, "H2O": 18.015}


@pytest.fixture(scope="module")
def streams() -> dict[str, dict]:
    sheet = yaml.safe_load((PROCESS / "process" / "flowsheet.yaml").read_text(encoding="utf-8"))
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


def test_the_stated_yield_and_benzotrichloride_use_follow_from_the_flowsheet(streams):
    btc = _components(streams["S4"])["BTC"] / MW["BTC"]
    product = _components(streams["S11"])
    yield_ = product["BZCL"] / MW["BZCL"] / (2.0 * btc)
    assert yield_ == pytest.approx(0.9719, abs=5e-5)
    assert "97.19 %" in _text("DESIGN.md")
    specific = streams["S4"]["flow"]["value"] / streams["S11"]["flow"]["value"]
    assert specific == pytest.approx(0.715, abs=5e-4)


def test_product_purity_and_acid_strength(streams):
    product = _components(streams["S11"])
    assert product["BZCL"] / sum(product.values()) > 0.995
    acid = _components(streams["S8"])
    assert acid["HCL"] / sum(acid.values()) == pytest.approx(0.30, abs=1e-3)


def test_the_column_split_closes_on_the_still_distillate(streams):
    s9 = _components(streams["S9"])
    out = {n: _components(streams["S11"]).get(n, 0.0) + _components(streams["S12"]).get(n, 0.0) for n in s9}
    for name, value in s9.items():
        assert out[name] == pytest.approx(value, rel=1e-3, abs=1e-4)


def test_not_published_in_the_change_that_adds_it():
    manifest = yaml.safe_load((PROCESS / "process.yaml").read_text(encoding="utf-8"))
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
        r"^\| (?:2\.7e-3 \(design\)|k/10|k/100) \| [^|]+ \| ([\d.]+) K \| [^|]+ \| [^|]+ \| [^|]+ \| ([^|]+) \|$",
        (PROCESS / "DESIGN.md").read_text(encoding="utf-8"),
        flags=re.M,
    )
    assert len(rows) == 3
    mtt = 471.0
    for mtsr, stated in rows:
        possible = {_criticality(float(mtsr), mtt, 300.0 + 0.5 * i) for i in range(600)}
        assert {int(c) for c in re.findall(r"\d", stated)} == possible, (mtsr, stated)
    assert "and 5 if it lies below (TD24 < 421.9 K" in _text("DESIGN.md")


def test_the_residue_is_drained_above_its_ideal_benzoic_acid_liquidus(streams):
    s13 = streams["S13"]
    assert s13["composition"]["basis"] == "mole_fraction"
    x_ba = s13["composition"]["values"]["BA"]
    tfus, dhfus, r = 395.2, 18000.0, 8.314  # NIST (SRC-2), as scripts/balance.py
    liquidus = 1.0 / (1.0 / tfus - r * math.log(x_ba) / dhfus)
    assert liquidus == pytest.approx(355.0, abs=0.5)
    assert s13["temperature"]["value"] - liquidus >= 15.0


def test_water_ingress_and_absorber_water_loss_are_open_items():
    # 1 kg of water with benzotrichloride: two HCl per water, as gas at 413 K and 101.325 kPa.
    volume = 1.0 / MW["H2O"] * 2.0 * 8.314 * 413.15 / 101.325
    assert volume == pytest.approx(3.8, abs=0.05)
    design = _text("DESIGN.md")
    assert "about 3.8 m3 at 413 K" in design
    assert "Loss of the absorber water while R-101 doses" in design
    equipment = _text("equipment/equipment-list.yaml")
    assert "anti-suck-back" in equipment and "A-101's water flow" in equipment
