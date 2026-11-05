"""benzoyl-chloride-1 (#156): the folder's stated numbers against its own flowsheet.

Fast, without core: the flowsheet's streams (propagated by core and given by
scripts/balance.py) are read as YAML, and the statements the folder makes in DESIGN.md and
process.yaml are checked against them:

- the yield on benzotrichloride (97.19 % of theory, two benzoyl chloride per benzotrichloride)
  and the specific benzotrichloride use (0.715 kg/kg) follow from S4 and S11;
- the product meets the patent's purity (above 99.5 %) and the absorber makes 30 wt% acid;
- the column's specified split K101 closes on the still's distillate S9;
- the process is not set public in the change that adds it (CONTRIBUTING, "Publishing a
  process").
"""

from __future__ import annotations

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
