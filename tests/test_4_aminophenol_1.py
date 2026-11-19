"""4-aminophenol-1 (#506): the folder's stated numbers against its own files.

Fast, without core: the flowsheet propagate wrote is read as data, and the statements the folder
makes in DESIGN.md, process.yaml, the recipe and lca.yaml are checked against it:

- the mass balance over the plant closes, and the design specifications hold (capacity, the
  charge's water per nitrobenzene, the nitrobenzene left after the hydrogenation);
- the yield and purity DESIGN.md and process.yaml state are the flowsheet's;
- the solubility points are SRC-4's mass fractions converted to kg per kg of water, and the
  stills' relative volatilities follow from SRC-5's solubilities and the vapour pressures;
- the heats of reaction follow from the formation enthalpies DESIGN.md names;
- the charge's heating Q1 is the hand calculation of D-009;
- the recipe's batch closes the flowsheet's product rate, and lca.yaml's carbon per batch
  follows SRC-1 and the recipe;
- the entry is public with CC-BY-4.0 and its chemicals are in the registry.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

KIT = Path(__file__).resolve().parents[1]
PROCESS = KIT / "processes" / "4-aminophenol-1"


def _yaml(rel: str) -> dict:
    return yaml.safe_load((PROCESS / rel).read_text(encoding="utf-8"))


def _text(rel: str) -> str:
    return " ".join((PROCESS / rel).read_text(encoding="utf-8").split())


@pytest.fixture(scope="module")
def components() -> dict:
    return {c["id"]: c for c in _yaml("process/materials.yaml")["components"]}


@pytest.fixture(scope="module")
def streams() -> dict:
    return {s["id"]: s for s in _yaml("process/flowsheet.yaml")["streams"]}


def _value(stream: dict, quantity: str) -> float:
    return stream["state"]["design"][quantity]["value"]


def _kg(stream: dict, components: dict) -> dict[str, float]:
    """kg/h of each component of a material stream."""
    state = stream["state"]["design"]
    flow = state["flow"]["value"]
    comp = state["composition"]
    values = comp["values"]
    if comp["basis"] == "mass_fraction":
        return {k: flow * v for k, v in values.items()}
    mw = sum(v * components[k]["molar_mass"] for k, v in values.items())
    return {k: flow * v * components[k]["molar_mass"] / mw for k, v in values.items()}


def _step(sid: str) -> dict:
    return next(s for s in _yaml("process/flowsheet.yaml")["steps"] if s["id"] == sid)


FEEDS = ("S1", "S2", "S3", "S5", "S10", "S23")
PRODUCTS = ("S26", "S14", "S8", "S28")


def test_plant_mass_balance_closes(streams):
    fed = sum(_value(streams[s], "flow") for s in FEEDS)
    out = sum(_value(streams[s], "flow") for s in PRODUCTS)
    assert out == pytest.approx(fed, rel=1e-4)


def test_design_specifications_hold(streams, components):
    assert _value(streams["S26"], "flow") * 7920 / 1000 == pytest.approx(1000, rel=1e-4)
    charge = _kg(streams["S4"], components)
    assert charge["H2O"] / charge["NB"] == pytest.approx(6.27, rel=1e-3)
    left = _kg(streams["S6"], components)["NB"]
    assert left / charge["NB"] == pytest.approx(0.12, rel=1e-3)


def test_yield_and_purity_stated(streams, components):
    product = _kg(streams["S26"], components)
    total = sum(product.values())
    pap = product["PAP_S"] + product.get("PAP", 0.0)
    nb = _kg(streams["S2"], components)["NB"]
    yield_ = pap / components["PAP"]["molar_mass"] / (nb / components["NB"]["molar_mass"])
    assert f"{100 * yield_:.1f} %" == "82.1 %"
    assert f"{100 * pap / total:.1f} wt%" == "99.5 wt%"
    assert "82.1 % of the fresh nitrobenzene" in _text("DESIGN.md")
    assert "82.1 % of the nitrobenzene" in _text("process.yaml")
    assert "99.5 wt%" in _text("process.yaml")


def test_solubility_points_are_src4_converted():
    merck = {273.15: 0.0039, 297.15: 0.0065, 303.15: 0.0080}
    for sid in ("CR101", "CR102", "W101"):
        points = dict(map(tuple, _step(sid)["crystallizer"]["solubility"]["points"]))
        for t, w in merck.items():
            assert points[t] == pytest.approx(w / (1 - w), abs=2e-6)


def test_relative_volatilities_follow_the_solubilities(components):
    def alpha(w_sat: float, mw: float, psat: float) -> float:
        x = (w_sat / mw) / (w_sat / mw + (1 - w_sat) / components["H2O"]["molar_mass"])
        return psat / x / 101.418

    nb = alpha(0.008, components["NB"]["molar_mass"], 2.814)
    an = alpha(0.064 / 1.064, components["AN"]["molar_mass"], 6.108)
    st101 = _step("ST101")["still"]["volatility"]["alpha"]
    st102 = _step("ST102")["still"]["volatility"]["alpha"]
    assert st101["NB"] == pytest.approx(nb, abs=0.1)
    assert st102["NB"] == pytest.approx(nb, abs=0.1)
    assert st102["AN"] == pytest.approx(an, abs=0.02)


def test_heats_of_reaction_from_formation_enthalpies():
    hf = {"NB": 12500, "PAP": -192814.5, "H2O": -285825, "AN": 31600, "H2SO4": -814000, "NH3": -45558, "AS": -1180900, "H2": 0}
    for r in _yaml("process/reactions.yaml")["reactions"]:
        dh = sum(nu * hf[c] for c, nu in r["stoichiometry"].items())
        assert r["heat_of_reaction"]["value"] == pytest.approx(dh, abs=1.0), r["id"]


def test_charge_heating_is_the_hand_calculation(streams, components):
    inlets = {"S1": 298.15, "S2": 298.15, "S3": 298.15, "S20": 333.15, "S21": 313.15, "S22": 298.15}
    sensible = 0.0
    for sid, t in inlets.items():
        for c, kg in _kg(streams[sid], components).items():
            sensible += kg / components[c]["molar_mass"] * components[c]["liquid_heat_capacity"] * (358.15 - t)
    acid = _kg(streams["S3"], components)["H2SO4"] / components["H2SO4"]["molar_mass"]
    q1 = (sensible - acid * 59200.0) / 3600.0
    assert _value(streams["Q1"], "duty") == pytest.approx(q1, abs=0.2)
    dilution = (650 * 4.202 + 110 * 1.073) * 22.5 / (110 * 0.965 / 98.072)
    assert dilution == pytest.approx(59200, rel=2e-3)


def test_recipe_batch_closes_the_flowsheet(streams):
    recipe = _yaml("process/recipe.yaml")
    batch = recipe["batch_size"]["value"]
    rate = _value(streams["S26"], "flow")
    assert batch / rate == pytest.approx(8.5, abs=0.002)
    batches = recipe["hours_per_year"]["value"] * rate / batch
    assert f"{batches:.1f}" == "931.8"
    lca = _yaml("lca/lca.yaml")
    assert f"{batch:.1f} kg per batch, {batches:.1f} batches a year" in lca["technology"]


def test_carbon_per_batch_follows_src1_and_the_recipe(streams):
    batch = _yaml("process/recipe.yaml")["batch_size"]["value"]
    carbon = 8.0 / 154.0 * batch
    consumable = next(c for c in _yaml("lca/lca.yaml")["consumables"] if c["id"] == "activated-carbon")
    assert consumable["per_batch"] == pytest.approx(carbon, abs=0.2)


def test_screening_numbers_are_recorded():
    text = _text("DESIGN.md")
    for fact in ("129.7 K", "0.37 %", "358.6 K", "373.12 K", "2.8 %", "361.8 K", "14 %", "376.5 K"):
        assert fact in text
    assert _step("R101")["hazard"]["mtt"] == 373.12


def test_mappings_name_library_producers():
    mappings = _yaml("lca/mappings.yaml")["exchanges"]
    for key, path in (("feed:ACIDF", "sulfuric-acid-1"), ("feed:H2F", "hydrogen-1"), ("feed:NH3F", "ammonia-1"), ("consumable:nitrogen", "asu-1")):
        dataset = mappings[key]["dataset"]
        assert dataset["path"] == f"processes/{path}/lca/dataset.yaml"
        assert (KIT / dataset["path"]).is_file()
        assert dataset["product"] in (KIT / dataset["path"]).read_text(encoding="utf-8")


def test_public_and_registered():
    manifest = _yaml("process.yaml")
    assert manifest["publication"] == {"status": "public", "license": "CC-BY-4.0"}
    slugs = {c["slug"] for c in yaml.safe_load((KIT / "chemicals" / "chemicals.yaml").read_text())["chemicals"]}
    for side in ("inputs", "outputs", "utilities"):
        for flow in manifest["chemistry"][side]:
            assert flow["chemical"] in slugs, flow["chemical"]
    assert re.search(r"requires: cheme-as-code>=1\.12", (PROCESS / "plant.yaml").read_text())
