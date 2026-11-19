"""phthalic-anhydride-1 (#480): the reactor, the emission calibration, the LCI and the texts.

Fast, without core: the flowsheet, the reactions, the materials and the LCI dataset are read as
YAML and the numbers DESIGN.md, process.yaml and the sources state are recomputed by hand.

- the reactor feed is 60 000 Nm3/h of air at 80 g/Nm3 o-xylene (US 8 859 459 B2: 4 Nm3/h per
  tube, up to 100 g/Nm3), and the PA in the reactor gas lies in EP 0 574 855 A2's 0.6-2 vol%;
- the reactor's parallel conversions add up to 99.9 % of the o-xylene, and every heat of reaction
  is the formation enthalpies of materials.yaml;
- R101's duty Q3 is core's conversion-step model (calculated);
- the off-gas carries AP-42's uncontrolled CO (151 kg/Mg) and less than its 69 kg/Mg of PA,
  maleic anhydride and benzoic acid; the oxidiser destroys 95 % (AP-42: about 95 %);
- the LCI's o-xylene per kg and the texts that state it;
- the source register names the packages and says their values are not open data (ADR 0037).
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

KIT = Path(__file__).resolve().parents[1]
PROCESS = KIT / "processes" / "phthalic-anhydride-1"
NM3_PER_KMOL = 22.414


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


def _kmol_h(stream: dict, materials: dict) -> dict[str, float]:
    state = _state(stream)
    x = state["composition"]["values"]
    assert state["composition"]["basis"] == "mole_fraction"
    mw = sum(v * materials[c]["molar_mass"] for c, v in x.items())
    total = state["flow"]["value"] / mw
    return {c: v * total for c, v in x.items()}


def _kg_h(stream: dict, materials: dict) -> dict[str, float]:
    return {c: n * materials[c]["molar_mass"] for c, n in _kmol_h(stream, materials).items()}


def test_the_feed_is_the_patents_air_rate_and_loading(model):
    materials, streams, _ = model
    air = _kmol_h(streams["S1"], materials)
    nm3_h = sum(air.values()) * NM3_PER_KMOL
    assert nm3_h == pytest.approx(60000.0, rel=1e-4)
    assert nm3_h / 15000 == pytest.approx(4.0, rel=1e-4)  # Nm3/h per tube (US 8 859 459 B2)
    ox = _state(streams["S4"])["flow"]["value"]
    assert ox == 4800.0
    assert ox * 1000 / nm3_h == pytest.approx(80.0, rel=1e-4)  # g/Nm3, below the patent's 100


def test_the_reactor_conversions_and_heats_follow_the_materials(model):
    materials, _, reactions = model
    r101 = ("PA_FORM", "MA_FORM", "BA_FORM", "OX_CO2", "OX_CO")
    assert sum(reactions[r]["conversion"]["value"] for r in r101) == pytest.approx(0.999, abs=1e-9)
    assert reactions["PA_FORM"]["conversion"]["value"] == 0.790
    assert reactions["MA_FORM"]["conversion"]["value"] == 0.035  # EP 0 574 855 A2: about 3.5 %
    for rid, reaction in reactions.items():
        hf = sum(n * materials[c]["ideal_gas"]["dHf_298"] for c, n in reaction["stoichiometry"].items())
        assert reaction["heat_of_reaction"]["value"] == pytest.approx(hf, abs=1.0), rid


def test_the_reactor_gas_and_duty(model):
    materials, streams, _ = model
    s6 = _state(streams["S6"])
    assert s6["flow"]["provenance"] == "calculated"
    y_pa = s6["composition"]["values"]["PA"]
    assert 0.006 <= y_pa <= 0.020  # EP 0 574 855 A2: 0.6-2.0 vol% PA in the effluent
    pa_kg = _kg_h(streams["S6"], materials)["PA"]
    assert pa_kg / 4800.0 == pytest.approx(1.102, abs=0.001)  # Jara et al. 2005: 1.10 kg/kg
    q3 = _state(streams["Q3"])["duty"]
    assert q3["provenance"] == "calculated"
    assert q3["source"].startswith("cheme process propagate: conversion duty R101")
    assert q3["value"] == pytest.approx(14444.6, abs=0.5)
    q4 = _state(streams["Q4"])["duty"]["value"]
    assert q3["value"] - q4 == pytest.approx(14294.6, abs=0.5)  # the enthalpy change alone


def test_the_off_gas_is_calibrated_to_ap42(model):
    materials, streams, _ = model
    product_t_h = _state(streams["S13"])["flow"]["value"] / 1000.0
    off = _kg_h(streams["S9"], materials)
    co_per_t = off["CO"] / product_t_h
    assert co_per_t == pytest.approx(151.0, rel=0.01)  # AP-42 Table 6.5-1, uncontrolled CO
    particulate = (off["PA"] + off["MA"] + off["BA"]) / product_t_h
    assert 55.0 < particulate < 69.0  # AP-42: 69 kg/Mg uncontrolled (PA, MA, benzoic acid)
    flue = _kg_h(streams["S16"], materials)
    for c in ("CO", "PA", "MA", "BA", "OX"):
        assert flue[c] / off[c] == pytest.approx(0.05, rel=1e-3), c  # 95 % destroyed
    assert flue["CO"] / product_t_h < 8.0  # AP-42 with a thermal incinerator: 8 kg/Mg


def test_the_product_and_the_yield(model):
    materials, streams, _ = model
    product = _kg_h(streams["S13"], materials)
    total = sum(product.values())
    assert total == pytest.approx(5055.4, abs=0.1)
    assert product["PA"] / total > 0.998  # AP-42: 99.8 wt% from the vacuum distillation
    assert total / 4800.0 == pytest.approx(1.0532, abs=1e-4)


def test_the_lci_o_xylene_per_kg_and_the_texts():
    dataset = _yaml("lca/dataset.yaml")
    exchanges = {e["key"]: e for e in dataset["exchanges"]}
    ox = exchanges["feed:OX"]["amount"]
    pan = exchanges["product:PAN"]["amount"]
    assert ox / pan == pytest.approx(0.9495, abs=5e-5)
    assert "0.9495 kg/kg" in _text("process.yaml")
    assert "o-xylene 0.9495 kg" in _text("DESIGN.md")
    lca = _yaml("lca/lca.yaml")
    assert lca["allocation"]["shares"] == {"PAN": 1.0, "HPS": 0.0, "LPS": 0.0}


def test_public_and_the_source_register_names_the_packages():
    manifest = _yaml("process.yaml")
    assert manifest["publication"] == {"status": "public", "license": "CC-BY-4.0"}
    row = next(line for line in (PROCESS / "DESIGN.md").read_text(encoding="utf-8").splitlines()
               if line.startswith("| SRC-8 |"))
    for needle in ("chemicals 1.5.2", "thermo 0.6.1", "Joback", "DIPPR_PERRY_8E", "WEBBOOK_HSUB",
                   "not open data", "ADR 0037", "not read here"):
        assert needle in row, needle
    assert "open data packages" not in row
