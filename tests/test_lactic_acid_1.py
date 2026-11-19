"""lactic-acid-1 (#517): the folder's stated numbers against its own flowsheet.

Fast and without core: the flowsheet's streams (propagated by core) are read as YAML, and the
statements the folder makes in process.yaml, the recipe, the reactions, lca/lca.yaml and the
mappings are checked against them:

- the specs hold: 100 000 t/a of lactic acid in 8000 h, the titer's calcium lactate fraction, 1.5
  mol of ethanol per mol of lactic acid and 12 mol of water per mol of ester, and the followers
  sit at their stated ratios to the syrup, which follow from the materials and reactions;
- the mixers create no heat: the hydrolysis feed is at its inlets' mixing temperature, and the
  medium water, from the same feed as the slaking water, is warmed by a stated steam duty;
- the product is 88 wt% lactic acid;
- the fermentation's conversions are the BioSTEAM model's, and the lactic acid formed reaches the
  product at about 92 %;
- the cakes hold the moistures of the source (35 and 20 wt%);
- the recipe's batch holds the flowsheet's year average of the broth;
- the hand duties' heater and condenser pairs are stated with their arithmetic;
- every heat stream reaches the LCI, the feeds' carbon is biogenic, and the ethanol holders have
  an emission exclusion;
- the stated specific consumptions follow from the streams;
- the process is public with CC-BY-4.0 and requires cheme-as-code 1.13.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

KIT = Path(__file__).resolve().parents[1]
PROCESS = KIT / "processes" / "lactic-acid-1"
LIQUIDS = ("H2O", "GLC", "LA", "CALA", "AA", "CAAC", "CAOH", "H2SO4", "ETOH", "ETLA")


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


def _duty(streams, sid: str) -> float:
    return streams[sid]["duty"]["value"]


def test_specs_hold(sheet, kg, streams, materials) -> None:
    specs = {s["id"]: s for s in sheet["specs"]}
    assert kg("S32")["LA"] * 8000 / 1000 == pytest.approx(100_000, rel=1e-4)
    assert specs["rate"]["target"]["value"] == 100000
    mw = {k: materials[k]["molar_mass"] for k in materials}
    titer = specs["titer"]["target"]["value"]
    broth = kg("S8")
    assert broth["CALA"] / sum(broth.values()) == pytest.approx(titer, rel=1e-4)
    # 130 g/L of lactic acid as calcium lactate (one per 2 lactic acid) at 1070 kg/m3
    assert 130 * mw["CALA"] / (2 * mw["LA"]) / 1070 == pytest.approx(titer, rel=1e-4)
    feed = kg("S20")
    assert (feed["ETOH"] / mw["ETOH"]) / (feed["LA"] / mw["LA"]) == pytest.approx(1.5, rel=1e-4)
    hyd = kg("S25")
    assert (hyd["H2O"] / mw["H2O"]) / (hyd["ETLA"] / mw["ETLA"]) == pytest.approx(12.0, rel=1e-4)
    syrup = streams["S1"]["flow"]["value"]
    for sid, ratio in specs["rate"]["vary"]["with"].items():
        assert streams[sid]["flow"]["value"] == pytest.approx(ratio * syrup, rel=1e-4), sid


def test_follower_ratios_follow_their_stated_basis(sheet, streams, materials) -> None:
    """Lime 10 % over the acids formed (and the CSL's acid), the acid 1.01 mol per mol of calcium,
    the slaking water for a 20 wt% Ca(OH)2 slurry: the flowsheet's follower ratios against the
    syrup's and CSL's compositions, the fermentation's conversions and the molar masses."""
    ratios = {s["id"]: s for s in sheet["specs"]}["rate"]["vary"]["with"]
    mw = {k: m["molar_mass"] for k, m in materials.items()}
    rxns = {r["id"]: r for r in _load("process/reactions.yaml")["reactions"]}
    syrup = streams["S1"]["composition"]["values"]
    csl = streams["S3"]["composition"]["values"]
    acid = streams["S11"]["composition"]["values"]
    glc = syrup["GLC"] / mw["GLC"]  # kmol of glucose per kg of syrup
    csl_la = ratios["S3"] * csl["LA"] / mw["LA"] / 2  # kmol of Ca for the CSL's lactic acid
    # FLA: 2 lactic acid per glucose, 1 Ca; FAA: 3 acetic acid per glucose, 1.5 Ca
    ca_per_glc = rxns["FLA"]["conversion"]["value"] + rxns["FAA"]["conversion"]["value"] * 1.5
    cao = (glc * ca_per_glc + csl_la) * 1.1
    assert cao * mw["CAO"] == pytest.approx(ratios["S4"], rel=2e-3)
    assert cao * 1.01 * mw["H2SO4"] / acid["H2SO4"] == pytest.approx(ratios["S11"], rel=2e-3)
    # a 20 wt% slurry of Ca(OH)2: water per kg of CaO
    water = (mw["CAOH"] / mw["CAO"] / 0.20 - 1) * ratios["S4"]
    assert water == pytest.approx(ratios["S5"], rel=2e-3)


def _heat_flow(kg, materials, sid: str) -> float:
    """A stream's heat capacity flow (kW/K) at the liquid heat capacities of materials.yaml."""
    return sum(
        m / materials[k]["molar_mass"] * materials[k]["liquid_heat_capacity"]
        for k, m in kg(sid).items()
    ) / 3600


def test_mixers_create_no_heat(kg, streams, materials) -> None:
    """M402 is adiabatic: S25 at the mixing temperature of S24 and S29; M101's medium water comes
    at the slaking water's temperature (one feed) and Q17 warms it to the medium's."""
    t = {s: streams[s]["temperature"]["value"] for s in ("S1", "S2", "S3", "S5", "S6", "S24", "S25", "S29")}
    a, b = _heat_flow(kg, materials, "S24"), _heat_flow(kg, materials, "S29")
    assert t["S25"] == pytest.approx((a * t["S24"] + b * t["S29"]) / (a + b), abs=0.05)
    assert t["S2"] == t["S5"]
    assert t["S1"] == t["S3"] == t["S6"]
    warm = _heat_flow(kg, materials, "S2") * (t["S6"] - t["S2"])
    assert _duty(streams, "Q17") == pytest.approx(warm, rel=1e-3)


def test_product_is_88_percent(kg) -> None:
    prod = kg("S32")
    assert prod["LA"] / sum(prod.values()) == pytest.approx(0.881, abs=0.002)
    assert prod.get("ETOH", 0.0) < 1e-6


def test_fermentation_conversions_are_the_sources() -> None:
    rxns = {r["id"]: r for r in _load("process/reactions.yaml")["reactions"]}
    assert rxns["FLA"]["conversion"]["value"] == 0.76
    assert rxns["FAA"]["conversion"]["value"] == 0.07
    assert rxns["FBIO"]["conversion"]["value"] == 0.02
    assert rxns["HYD"]["conversion"]["value"] == 0.80
    assert "ASSUMED" in rxns["EST"]["conversion"]["source"]


def test_recovery_about_92_percent(kg) -> None:
    """Lactic acid formed (glucose x 0.76 x 2, and the CSL's) against the product's."""
    glucose_in = kg("S1")["GLC"]
    formed = glucose_in * 0.76 * 2 * 90.078 / 180.156 + kg("S3")["LA"]
    assert kg("S32")["LA"] / formed == pytest.approx(0.92, abs=0.005)


@pytest.mark.parametrize(("cake", "moisture"), [("S9", 0.35), ("S13", 0.20)])
def test_cake_moisture(kg, cake, moisture) -> None:
    flows = kg(cake)
    liquid = sum(v for k, v in flows.items() if k in LIQUIDS)
    assert liquid / sum(flows.values()) == pytest.approx(moisture, abs=0.005)


def test_recipe_holds_the_broth(streams) -> None:
    recipe = _load("process/recipe.yaml")
    (up,) = recipe["unit_procedures"]
    occupancy = sum(op["duration"]["value"] for op in up["operations"])
    assert occupancy == pytest.approx(130 / 0.89 + 12, abs=0.01)
    cycle = occupancy / up["parallel"]
    rate = recipe["batch_size"]["value"] * 1000 / cycle
    assert rate == pytest.approx(streams["S8"]["flow"]["value"], rel=0.01)
    assert recipe["hours_per_year"]["value"] == 8000


def test_hand_duties_state_their_arithmetic(sheet) -> None:
    hand = {"Q4", "Q5", "Q7", "Q8", "Q9", "Q10", "Q12", "Q13", "Q14", "Q15", "Q16"}
    for s in sheet["streams"]:
        if s["id"] in hand:
            duty = s["state"]["design"]["duty"]
            assert duty["provenance"] == "assumed"
            assert duty["source"].startswith("D-009 hand estimate"), s["id"]
        if s["id"] == "Q17":
            assert s["state"]["design"]["duty"]["source"].startswith("D-005 hand estimate")
    calc = {"Q1", "Q2", "Q3", "Q6", "Q11"}
    for s in sheet["streams"]:
        if s["id"] in calc:
            assert s["state"]["design"]["duty"]["provenance"] == "calculated", s["id"]


def test_heater_condenser_pairs_close(streams) -> None:
    """Each column's reboiler and condenser differ by its streams' sensible heat only (small)."""
    for reb, cond in (("Q7", "Q8"), ("Q9", "Q10"), ("Q12", "Q13")):
        assert abs(_duty(streams, reb) - _duty(streams, cond)) < 0.25 * _duty(streams, cond)


def test_lca_covers_every_heat_stream_and_biogenic_carbon(sheet) -> None:
    lca = _load("lca/lca.yaml")
    flows = {f["key"]: f for f in lca["flows"]}
    for key in ("feed:LPS", "feed:MPS", "product:CW", "feed:POWER"):
        assert key in flows
    lps = flows["feed:LPS"]["source"]
    for q in ("Q4", "Q6", "Q9", "Q11", "Q12", "Q14", "Q17"):
        assert q in lps
    cw = flows["product:CW"]["source"]
    for q in ("Q1", "Q2", "Q3", "Q5", "Q8", "Q10", "Q13", "Q15", "Q16"):
        assert q in cw
    content = lca["carbon_accounting"]["content"]
    for key in ("feed:GLCF", "feed:CSLF", "feed:ETOHF"):
        assert content[key]["biogenic_fraction"] == 1.0
    excluded = {e for x in lca["emission_exclusions"] for e in x.get("equipment", [])}
    for tag in ("R-401", "C-401", "C-402", "C-403", "R-402", "E-404"):
        assert tag in excluded
    assert {c["id"] for c in lca["consumables"]} == {"cip-water", "cip-caustic"}
    # the esterifier's resin and the fermenters' steaming are cut off with their amounts
    cut = {c["id"]: c for c in lca["cutoff"]}
    assert cut["amberlyst-15"]["catalyst"] is True
    s20 = {s["id"]: s for s in sheet["streams"]}["S20"]["state"]["design"]["flow"]["value"]
    # SRC-1's charge: 3.9 wt% of one hour's feed mass, replaced once a year
    assert cut["amberlyst-15"]["per_year"] == pytest.approx(0.039 * s20, rel=0.01)
    assert cut["fermenter-sip-steam"]["per_year"] > 0


def test_mappings_link_library_producers() -> None:
    maps = _load("lca/mappings.yaml")["exchanges"]
    assert maps["feed:LIMEF"]["dataset"]["path"].startswith("processes/lime-1/")
    assert maps["feed:ACIDF"]["dataset"]["path"] == "processes/sulfuric-acid-1/lca/dataset.yaml"
    assert maps["feed:ETOHF"]["dataset"]["path"] == "processes/bioethanol-1/lca/dataset.yaml"
    for key in ("feed:LIMEF", "feed:ACIDF", "feed:ETOHF"):
        assert (KIT / maps[key]["dataset"]["path"]).is_file()
    # the sugar residue is not tagged as wastewater, so it is not linked to activated sludge
    assert "product:RES" not in maps
    outputs = {o["inventory_key"]: o for o in _load("process.yaml")["chemistry"]["outputs"]}
    assert outputs["product:RES"]["chemical"] == "sugar-residue"


def test_specific_consumptions(kg, streams) -> None:
    la = kg("S32")["LA"]
    assert kg("S1")["GLC"] / la == pytest.approx(1.40, abs=0.01)
    assert kg("S4")["CAO"] / la == pytest.approx(0.42, abs=0.01)
    assert kg("S11")["H2SO4"] / la == pytest.approx(0.75, abs=0.01)
    assert streams["S13"]["flow"]["value"] / la == pytest.approx(1.61, abs=0.01)
    steam = sum(_duty(streams, q) for q in ("Q4", "Q6", "Q7", "Q9", "Q11", "Q12", "Q14", "Q17"))
    assert steam / la == pytest.approx(4.09, abs=0.02)
    text = _text("README.md")
    for figure in ("1.40 kg", "0.42 kg", "0.75 kg", "4.09 kWh", "1.61 kg"):
        assert figure in text


def test_manifest() -> None:
    manifest = _load("process.yaml")
    assert manifest["publication"] == {"status": "public", "license": "CC-BY-4.0"}
    assert manifest["maturity"] == "concept"
    outputs = {o["chemical"]: o for o in manifest["chemistry"]["outputs"]}
    assert outputs["lactic-acid"]["role"] == "main-product"
    assert outputs["lactic-acid"]["inventory_key"] == "product:LAP"
    plant = _load("plant.yaml")
    assert plant["requires"] == "cheme-as-code>=1.13"
    assert "#517" in plant["description"]
