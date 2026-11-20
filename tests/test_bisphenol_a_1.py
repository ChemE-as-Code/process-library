"""bisphenol-a-1 (#510): the reactor, the crystallizer, the recycle, the LCI and the texts.

Fast, without core: the flowsheet, the reactions, the materials and the LCI dataset are read as
YAML and the numbers DESIGN.md, process.yaml and the sources state are recomputed by hand.

- the reactor's parallel conversions add up to US 4 391 997 A's 69 % of the acetone and split it
  as that patent's Table I, example 3 (95.40 / 3.80 / 0.80 wt% of the products);
- the reactor inlet holds phenol to acetone 10 mol/mol (design spec ratio), its effluent's
  bisphenol A lies in US 5 723 688 A's 15-26 wt%, and R101's duty is core's model;
- the crystallizer's feed water and acetone lie in US 5 723 688 A's ranges, its yield is 0.75, its
  duty is core's and the latent heat of what evaporates matches it plus the vapour's own cooling;
  it runs below 1 kPa(a) and the booster and condensers' heat (Q15) closes the balance;
- the condensate column's duties close on its streams, and the phenol stripper has its steam;
- the wash is 0.6 kg of phenol per kg of adduct (US 5 723 688 A, example 1), the mother liquor's
  bisphenol A lies in US 4 391 997 A's 5-15 wt%;
- the product is 70 kt/a at 8000 h and inside the EU risk assessment's commercial purity;
- the LCI's phenol and acetone per kg, their links to acetone-1 and the texts that state them;
- the source register names the packages and says their values are not open data (ADR 0037).
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

KIT = Path(__file__).resolve().parents[1]
PROCESS = KIT / "processes" / "bisphenol-a-1"


def _yaml(rel: str) -> dict:
    return yaml.safe_load((PROCESS / rel).read_text(encoding="utf-8"))


def _text(rel: str) -> str:
    return " ".join((PROCESS / rel).read_text(encoding="utf-8").split())


@pytest.fixture(scope="module")
def model():
    materials = {c["id"]: c for c in _yaml("process/materials.yaml")["components"]}
    streams = {s["id"]: s for s in _yaml("process/flowsheet.yaml")["streams"]}
    reactions = {r["id"]: r for r in _yaml("process/reactions.yaml")["reactions"]}
    return materials, streams, reactions


def _state(stream: dict) -> dict:
    return stream["state"]["design"]


def _kg_h(stream: dict, materials: dict) -> dict[str, float]:
    state = _state(stream)
    flow = state["flow"]["value"]
    comp = state["composition"]
    x = comp["values"]
    if comp["basis"] == "mass_fraction":
        return {c: v * flow for c, v in x.items()}
    assert comp["basis"] == "mole_fraction"
    mw = sum(v * materials[c]["molar_mass"] for c, v in x.items())
    return {c: v * materials[c]["molar_mass"] / mw * flow for c, v in x.items()}


def _kmol_h(stream: dict, materials: dict) -> dict[str, float]:
    return {c: m / materials[c]["molar_mass"] for c, m in _kg_h(stream, materials).items()}


def test_the_reactor_conversions_follow_the_patent(model):
    materials, _, reactions = model
    r101 = ("BPA_FORM", "OPBPA_FORM", "DIANIN_FORM")
    assert sum(reactions[r]["conversion"]["value"] for r in r101) == pytest.approx(0.69, abs=1e-5)
    # US 4 391 997 A, Table I, example 3: wt% of the products -> moles of acetone
    pp, op, others = 95.40 / 228.286, 3.80 / 228.286, 2 * 0.80 / 268.35
    total = pp + op + others
    assert reactions["BPA_FORM"]["conversion"]["value"] == pytest.approx(0.69 * pp / total, abs=2e-6)
    assert reactions["OPBPA_FORM"]["conversion"]["value"] == pytest.approx(0.69 * op / total, abs=2e-6)
    for rid, reaction in reactions.items():
        stoich = reaction["stoichiometry"]
        mass = sum(n * materials[c]["molar_mass"] for c, n in stoich.items())
        assert mass == pytest.approx(0.0, abs=0.01), rid  # mass balanced
    # BPA_FORM's heat from the formation enthalpies of DESIGN.md D-006 (chemicals 1.5.2)
    hf_bpa_l = -368.6 + 26.84
    hf_phenol_l = -165.1 + 11.51
    dh = hf_bpa_l - 285.825 - 2 * hf_phenol_l - (-248.4)
    assert reactions["BPA_FORM"]["heat_of_reaction"]["value"] == pytest.approx(dh * 1000, abs=50)


def test_the_reactor_feed_effluent_and_duty(model):
    materials, streams, _ = model
    feed = _kmol_h(streams["S8"], materials)
    assert feed["PHENOL"] / feed["ACETONE"] == pytest.approx(10.0, rel=1e-5)  # design spec ratio
    eff = _kg_h(streams["S9"], materials)
    w_bpa = eff["BPA"] / sum(eff.values())
    assert 0.15 <= w_bpa <= 0.26  # US 5 723 688 A: preferably 15-26 wt%
    assert w_bpa == pytest.approx(0.185, abs=0.001)
    assert _state(streams["S9"])["temperature"]["value"] == 353.15  # 80 C, last bed (US 4 391 997 A)
    q2 = _state(streams["Q2"])["duty"]
    assert q2["provenance"] == "calculated"
    assert q2["source"].startswith("cheme process propagate: conversion duty R101")
    assert 0.0 < q2["value"] < 100.0  # the beds run almost adiabatic (D-005)


def test_the_crystallizer_feed_duty_and_evaporation(model):
    materials, streams, _ = model
    feed = _kg_h(streams["S11"], materials)
    total = sum(feed.values())
    assert 0.02 <= feed["H2O"] / total <= 0.12  # US 5 723 688 A: preferably 2-12 wt% water
    assert 0.001 <= feed["ACETONE"] / total <= 0.08  # 0.1-8 wt% acetone
    slurry = _kg_h(streams["S14"], materials)
    liquor = _kg_h(streams["S13"], materials)
    crystallized = slurry["ADDUCT"] * 228.286 / 322.397
    assert crystallized / liquor["BPA"] == pytest.approx(0.75, rel=1e-5)  # imposed yield
    q4 = _state(streams["Q4"])["duty"]
    assert q4["provenance"] == "calculated"
    vap = _kg_h(streams["S12"], materials)
    latent = (vap["H2O"] * 43128 / 18.015 + vap["ACETONE"] * 29820 / 58.079
              + vap["PHENOL"] * 56318 / 94.111) / 3600
    # the water dose's basis (D-007): the latent heat at 318 K takes Q4 plus the evaporated
    # material's own cooling from the feed temperature
    t_feed = _state(streams["S11"])["temperature"]["value"]
    vap_kmol = _kmol_h(streams["S12"], materials)
    own = sum(n * materials[c]["liquid_heat_capacity"] for c, n in vap_kmol.items()) * (t_feed - 318.15) / 3600
    assert latent == pytest.approx(q4["value"] + own, rel=0.005)
    # the crystallizer runs at its mother liquor's bubble pressure (below 1 kPa), the vapour is
    # boosted to 12 kPa(a) and condensed; Q15 books the rest of the condensers' heat (D-007)
    assert _state(streams["S13"])["pressure"]["value"] < 1.0
    assert _state(streams["S12"])["pressure"]["value"] == 12.0
    q14 = _state(streams["Q14"])["duty"]["value"]
    q15 = _state(streams["Q15"])["duty"]["value"]
    subcool = sum(n * materials[c]["liquid_heat_capacity"] for c, n in vap_kmol.items()) * (318.15 - 313.15) / 3600
    assert q15 == pytest.approx(latent - q4["value"] + subcool + q14, abs=0.5)


def test_the_condensate_column_closes_and_the_stripper_has_steam(model):
    materials, streams, _ = model
    # C401: no feed-bottoms exchange, so Q12 - Q13 is the products' sensible heat above the feed
    t_feed = _state(streams["S12"])["temperature"]["value"]
    sensible = sum(
        sum(n * materials[c]["liquid_heat_capacity"] for c, n in _kmol_h(streams[s], materials).items())
        * (_state(streams[s])["temperature"]["value"] - t_feed) for s in ("S27", "S28")) / 3600
    q12 = _state(streams["Q12"])["duty"]["value"]
    q13 = _state(streams["Q13"])["duty"]["value"]
    assert q12 - q13 == pytest.approx(sensible, abs=1.0)
    # C301: a steam-stripping section below the flash zone (D-009)
    steam = streams["S29"]
    assert steam["to"] == "C301.steam" and _state(steam)["phase"]["value"] == "vapor"
    assert 13.6 < _state(steam)["flow"]["value"] < 100.0  # above the Kremser minimum


def test_the_wash_and_the_mother_liquor(model):
    materials, streams, _ = model
    cake = _kg_h(streams["S15"], materials)
    wash = _state(streams["S5"])["flow"]["value"]
    assert wash / cake["ADDUCT"] == pytest.approx(0.6, rel=1e-4)  # US 5 723 688 A, example 1
    ml = _kg_h(streams["S16"], materials)
    assert 0.05 <= ml["BPA"] / sum(ml.values()) <= 0.15  # US 4 391 997 A: 5-15 wt%


def test_the_product_rate_and_purity(model):
    materials, streams, _ = model
    product = _kg_h(streams["S26"], materials)
    total = sum(product.values())
    assert total * 8000 / 1000 == pytest.approx(70000.0, rel=1e-4)  # design spec rate
    assert product["BPA"] / total > 0.998  # EU RAR: commercial purity 99-99.8 %
    assert product["PHENOL"] / total < 0.0006  # EU RAR: phenol below 0.06 %
    assert product["OPBPA"] / total < 0.002  # isomers below 0.2 %


def test_the_lci_feeds_per_kg_their_links_and_the_texts():
    dataset = _yaml("lca/dataset.yaml")
    exchanges = {e["key"]: e for e in dataset["exchanges"]}
    bpa = exchanges["product:BPAP"]["amount"]
    phenol = exchanges["feed:PH"]["amount"] / bpa
    acetone = exchanges["feed:AC"]["amount"] / bpa
    assert phenol == pytest.approx(0.8619, abs=5e-5)
    assert acetone == pytest.approx(0.2641, abs=5e-5)
    assert phenol > 2 * 94.111 / 228.286 and acetone > 58.079 / 228.286  # above stoichiometry
    assert "0.8619 kg/kg" in _text("process.yaml")
    assert "phenol 0.8619 kg, acetone 0.2641 kg" in _text("DESIGN.md")
    links = _yaml("lca/mappings.yaml")["exchanges"]
    assert links["feed:PH"]["dataset"] == {"path": "processes/acetone-1/lca/dataset.yaml", "product": "product:PHENOL"}
    assert links["feed:AC"]["dataset"] == {"path": "processes/acetone-1/lca/dataset.yaml", "product": "product:ACETONE"}
    producer = {e["key"] for e in yaml.safe_load(
        (KIT / "processes" / "acetone-1" / "lca" / "dataset.yaml").read_text(encoding="utf-8"))["exchanges"]}
    assert {"product:PHENOL", "product:ACETONE"} <= producer


def test_public_and_the_source_register_names_the_packages():
    manifest = _yaml("process.yaml")
    assert manifest["publication"] == {"status": "public", "license": "CC-BY-4.0"}
    row = next(line for line in (PROCESS / "DESIGN.md").read_text(encoding="utf-8").splitlines()
               if line.startswith("| SRC-7 |"))
    for needle in ("chemicals 1.5.2", "thermo 0.6.1", "Joback", "DIPPR_PERRY_8E", "Rowlinson-Bondi",
                   "not open data", "ADR 0037", "none of the works"):
        assert needle in row, needle
    design = _text("DESIGN.md")
    for decision in ("D-001", "Rejected:", "L-1", "L-4"):
        assert decision in design, decision
