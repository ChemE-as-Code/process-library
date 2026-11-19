"""acetylsalicylic-acid-1 (#476): the folder's stated numbers against its own flowsheet.

Fast and without core: the flowsheet's streams (propagated by core, the hand values given) are
read as YAML, and the statements the folder makes in DESIGN.md, README.md, process.yaml and
lca/lca.yaml are checked against them:

- the yield on the salicylic acid (94.8 %), the purity (99.85 wt%) and the specific
  consumptions follow from S1, S2, S6, S15, S22 and S23;
- the heat of reaction is Hess's law on the NIST WebBook values DESIGN.md SRC-5 names, the rate
  constant's A gives the stated k at 358.15 K, and the solubility is SRC-1 Example I's lower end;
- the mixers' temperatures (S4, S12, S18, S20) are the adiabatic mixes of their inlets, and the
  hand duties Q1, Q5, Q7 and Q8 follow from the stream table and materials.yaml;
- the recycle fraction lies inside US 2 987 539 A's 30 to 70 %, and the wash ratio is 0.4 kg per
  kg of crystals;
- the recipe's batch size over the cycle the feeds state is the flowsheet's product rate;
- the allocation shares are the products' values at the stated relative prices;
- every heat stream reaches the LCI, the MTT exceeds every heating medium of R-101, and the
  tempered water stays above 283 K;
- the registry names the product and the salicylic acid; the process is public with CC-BY-4.0
  and requires cheme-as-code 1.12.
"""

from __future__ import annotations

import math
from pathlib import Path

import pytest
import yaml

KIT = Path(__file__).resolve().parents[1]
PROCESS = KIT / "processes" / "acetylsalicylic-acid-1"

MW = {"ACOH": 60.052, "AC2O": 102.089, "SA": 138.122, "ASA": 180.159, "ASA_S": 180.159, "H2SO4": 98.072}
CYCLE = 11.5655  # h, cheme process recipe (D-003), stated in the feeds' sources
METAL_R101, METAL_F101 = 4000.0, 5000.0  # kJ/K, ASSUMED (D-008, D-010)


def _yaml(rel: str) -> dict:
    return yaml.safe_load((PROCESS / rel).read_text(encoding="utf-8"))


def _text(rel: str) -> str:
    return " ".join((PROCESS / rel).read_text(encoding="utf-8").split())


@pytest.fixture(scope="module")
def sheet() -> dict:
    return _yaml("process/flowsheet.yaml")


@pytest.fixture(scope="module")
def materials() -> dict[str, dict]:
    return {c["id"]: c for c in _yaml("process/materials.yaml")["components"]}


@pytest.fixture(scope="module")
def streams(sheet) -> dict[str, dict]:
    return {s["id"]: s["state"]["design"] for s in sheet["streams"] if "state" in s}


def _kg(streams: dict, sid: str) -> dict[str, float]:
    """kg/h of each component of a stream."""
    st = streams[sid]
    flow = st["flow"]["value"]
    comp = st["composition"]
    values = comp["values"]
    if comp["basis"] == "mole_fraction":
        mm = sum(x * MW[c] for c, x in values.items())
        return {c: flow * x * MW[c] / mm for c, x in values.items()}
    return {c: flow * x for c, x in values.items()}


def _cp(streams: dict, materials: dict, sid: str) -> float:
    """Heat capacity flow, kJ/(K h), from the components' liquid heat capacities."""
    return sum(m / MW[c] * materials[c]["liquid_heat_capacity"] for c, m in _kg(streams, sid).items())


def _duty(streams: dict, qid: str) -> float:
    return streams[qid]["duty"]["value"]


def _temp(streams: dict, sid: str) -> float:
    return streams[sid]["temperature"]["value"]


def test_the_stated_yield_purity_and_consumptions_follow_from_the_flowsheet(streams):
    product = _kg(streams, "S15")
    p = sum(product.values())
    aspirin = product["ASA"] + product["ASA_S"]
    sa_fed = _kg(streams, "S1")["SA"]
    assert aspirin / MW["ASA"] / (sa_fed / MW["SA"]) == pytest.approx(0.948, abs=0.0005)
    assert aspirin / p == pytest.approx(0.9985, abs=0.00005)
    assert product["SA"] / p == pytest.approx(0.00037, abs=0.000005)
    assert product["H2SO4"] / p == pytest.approx(0.00018, abs=0.000005)
    assert sa_fed / p == pytest.approx(0.807, abs=0.0005)
    assert sum(_kg(streams, "S6").values()) / p == pytest.approx(0.627, abs=0.0005)
    assert sum(_kg(streams, "S2").values()) / p * 1000 == pytest.approx(0.88, abs=0.005)
    acid = _kg(streams, "S23")
    assert sum(acid.values()) / p == pytest.approx(0.351, abs=0.0005)
    assert acid["ACOH"] / sum(acid.values()) == pytest.approx(0.941, abs=0.0005)
    residue = _kg(streams, "S22")
    assert sum(residue.values()) / p == pytest.approx(0.084, abs=0.0005)
    assert residue["ASA"] / sum(residue.values()) == pytest.approx(0.62, abs=0.005)
    # the residue's aspirin is the loss: 5.0 % of the salicylic acid
    assert residue["ASA"] / MW["ASA"] / (sa_fed / MW["SA"]) == pytest.approx(0.050, abs=0.0005)
    for text in (_text("README.md"), _text("process.yaml")):
        assert "94.8 %" in text and "99.85 wt%" in text


def test_the_feeds_are_the_per_batch_amounts_over_the_cycle(streams):
    assert sum(_kg(streams, "S1").values()) * CYCLE == pytest.approx(10.0 * MW["SA"], abs=0.05)
    assert sum(_kg(streams, "S6").values()) * CYCLE == pytest.approx(10.5 * MW["AC2O"], abs=0.05)
    assert sum(_kg(streams, "S2").values()) * CYCLE == pytest.approx(1.5, abs=0.001)
    # the wash: 0.4 kg recovered acid per kg of crystals in the cake S9
    crystals = _kg(streams, "S9")["ASA_S"]
    assert streams["S11"]["flow"]["value"] / crystals == pytest.approx(0.4, abs=0.001)


def test_recipe_basis_and_capacity(streams):
    recipe = _yaml("process/recipe.yaml")
    batch = recipe["batch_size"]["value"]
    rate = streams["S15"]["flow"]["value"]
    assert batch / rate == pytest.approx(CYCLE, rel=2e-4)
    batches = rate * recipe["hours_per_year"]["value"] / batch
    assert batches == pytest.approx(684.8, abs=0.1)
    assert rate * recipe["hours_per_year"]["value"] / 1000 == pytest.approx(1171.5, abs=0.5)
    lca = _text("lca/lca.yaml")
    assert "1710.65 kg per batch, 684.8 batches a year" in lca


def test_heat_of_reaction_is_hess_law_on_the_nist_values():
    acetic, anhydride, water, hydrolysis_asa = -483.52, -625.0, -285.83, -27.2  # kJ/mol, SRC-5
    anhydride_hydrolysis = 2 * acetic - anhydride - water
    assert anhydride_hydrolysis == pytest.approx(-56.21, abs=0.005)
    reaction = _yaml("process/reactions.yaml")["reactions"][0]
    assert reaction["heat_of_reaction"]["value"] / 1000 == pytest.approx(
        anhydride_hydrolysis - hydrolysis_asa, abs=0.005
    )


def test_rate_constant_gives_the_stated_k_at_the_reaction_temperature():
    rate = _yaml("process/reactions.yaml")["reactions"][0]["rate"]
    k = float(rate["k"]["A"]) * math.exp(-float(rate["k"]["Ea"]) / (8.314 * 358.15))  # PyYAML reads 8.687e5 as text
    assert k == pytest.approx(1.541e-3, rel=1e-3)


def test_solubility_is_the_lower_end_of_the_source_example(sheet):
    cr101 = next(s for s in sheet["steps"] if s["id"] == "CR101")
    # US 2 731 492 A, Example I: 180 kg aspirin with 1800 kg acetic acid and 4.0 kg sulfuric acid
    assert cr101["crystallizer"]["solubility"]["value"] == pytest.approx(180 / 1804, abs=5e-5)


def test_mixing_temperatures_are_the_adiabatic_mixes(streams, materials):
    def mix(*pairs):
        return sum(_cp(streams, materials, s) * t for s, t in pairs) / sum(
            _cp(streams, materials, s) for s, _ in pairs
        )

    assert _temp(streams, "S12") == pytest.approx(mix(("S9", 293.15), ("S11", 303.15)), abs=0.02)
    t18 = mix(("S10", 293.15), ("S14", _temp(streams, "S14")))
    assert _temp(streams, "S18") == pytest.approx(t18, abs=0.02)
    assert _temp(streams, "S3") == _temp(streams, "S18")
    t4 = mix(("S1", 298.15), ("S2", 298.15), ("S3", _temp(streams, "S3")))
    assert _temp(streams, "S4") == pytest.approx(t4, abs=0.02)
    t20 = mix(("S19", _temp(streams, "S19")), ("S17", 303.15))
    assert _temp(streams, "S20") == pytest.approx(t20, abs=0.02)


def test_hand_duties_follow_from_the_stream_table(streams, materials):
    latent = {"ACOH": 394.7, "AC2O": 433.0}  # kJ/kg, D101's latent heats (materials.yaml)
    for c, value in latent.items():
        per_kmol = materials[c]["heat_of_vaporization"] / MW[c]
        assert per_kmol == pytest.approx(value, abs=0.05)
    q1 = _cp(streams, materials, "S4") * (358.15 - _temp(streams, "S4")) + METAL_R101 * (358.15 - 293.15) / CYCLE
    assert _duty(streams, "Q1") == pytest.approx(q1 / 3600, rel=1e-3)

    def condensed(sid, t_in, t_out):
        kg = _kg(streams, sid)
        return sum(kg.get(c, 0.0) * v for c, v in latent.items()) + _cp(streams, materials, sid) * (t_in - t_out)

    assert _duty(streams, "Q5") == pytest.approx(condensed("S16", 333.15, 303.15) / 3600, rel=1e-3)
    still_mean = (339.22 + 355.28) / 2  # cheme process stills
    assert _duty(streams, "Q7") == pytest.approx(condensed("S21", still_mean, 303.15) / 3600, rel=1e-3)
    q8 = _cp(streams, materials, "S15") * (333.15 - 313.15) + METAL_F101 * (333.15 - _temp(streams, "S13")) / CYCLE
    assert _duty(streams, "Q8") == pytest.approx(q8 / 3600, rel=1e-3)


def test_recycle_fraction_inside_the_source_range(sheet):
    x201 = next(s for s in sheet["steps"] if s["id"] == "X201")
    assert 0.3 <= x201["split"]["rec"] <= 0.7  # US 2 987 539 A, claims: 30 to 70 %
    tears = {t["stream"] for t in sheet["tears"]}
    assert tears == {"S3", "S11"}


def test_allocation_shares_are_the_values_at_the_stated_prices(streams):
    alloc = _yaml("lca/lca.yaml")["allocation"]
    value = {"PROD": streams["S15"]["flow"]["value"] * 1.0, "ACID": streams["S23"]["flow"]["value"] * 0.1}
    total = sum(value.values())
    for product, share in alloc["shares"].items():
        assert share == pytest.approx(value[product] / total, abs=0.0005)
    assert sum(alloc["shares"].values()) == pytest.approx(1.0)
    mass = streams["S15"]["flow"]["value"] / (streams["S15"]["flow"]["value"] + streams["S23"]["flow"]["value"])
    assert mass == pytest.approx(0.740, abs=0.0005)


def test_every_heat_stream_reaches_the_lci(sheet):
    lca = _text("lca/lca.yaml")
    for s in sheet["streams"]:
        if s.get("kind") == "energy":
            assert s["id"] in lca, s["id"]


def test_heating_media_stay_below_the_mtt_and_the_chilled_water_above_283_k():
    recipe = _yaml("process/recipe.yaml")
    jacket = next(u for u in recipe["unit_procedures"] if u["id"] == "REACT")["vessel"]["jacket"]
    mtt = 391.2  # acetic acid's normal boiling point, core's default MTT (D-011)
    assert jacket["heating_temperature"] < mtt
    assert jacket["coolant_temperature"] == pytest.approx((283.15 + 288.15) / 2)
    design = _text("DESIGN.md")
    for figure in ("MTSR 365.5 K", "380.4 K", "400.6 K", "404.8 K", "19.5 %"):
        assert figure in design


def test_registry_names_the_product_and_the_feed():
    registry = yaml.safe_load((KIT / "chemicals" / "chemicals.yaml").read_text(encoding="utf-8"))
    slugs = {c["slug"]: c for c in registry["chemicals"]}
    assert slugs["acetylsalicylic-acid"]["cas"] == "50-78-2"
    assert slugs["salicylic-acid"]["cas"] == "69-72-7"
    chemistry = _yaml("process.yaml")["chemistry"]
    names = {e["chemical"] for group in chemistry.values() for e in group}
    assert {"acetylsalicylic-acid", "salicylic-acid", "acetic-anhydride", "acetic-acid"} <= names


def test_public_and_requires_core_1_12():
    manifest = _yaml("process.yaml")
    assert manifest["publication"] == {"status": "public", "license": "CC-BY-4.0"}
    assert _yaml("plant.yaml")["requires"] == "cheme-as-code>=1.12"
