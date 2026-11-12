"""formic-acid-1 (#396, #433): the hydrolyser duty and the source register.

Fast, without core: the flowsheet and the materials are read as YAML and the duty of core's
conversion-step model (ADR 0059 of core) is recomputed by hand.

- R-201 is a liquid step: its streams are brought to and from 298.15 K at the components' liquid
  heat capacities (materials.yaml, the CRC Cpl packaged in chemicals 1.5.2), not at their
  ideal-gas ones (review of PR 436); Q10 is that model's duty, written by propagate;
- the heat of hydrolysis is the CRC liquid formation enthalpies' +7.7 kJ/mol at 298.15 K;
- the LP steam exchange of the LCI is the sum of its energy streams, and DESIGN.md / process.yaml
  state that sum per kg;
- SRC-7 names the packages, versions and tables and says the values are not open data
  (library ADR 0037, #433).
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

KIT = Path(__file__).resolve().parents[1]
PROCESS = KIT / "processes" / "formic-acid-1"
T0 = 298.15
LIQUID = ("MF", "MEOH", "H2O", "FA")
CAS = {"MF": "107-31-3", "MEOH": "67-56-1", "H2O": "7732-18-5", "FA": "64-18-6"}
LPS_STREAMS = ("Q6", "Q9", "Q10", "Q11", "Q13", "Q15", "Q17")
PRODUCT_KG_H = 6250.0


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


def _kmol_h(stream: dict, materials: dict) -> dict[str, float]:
    state = stream["state"]["design"]
    x = state["composition"]["values"]
    assert state["composition"]["basis"] == "mole_fraction"
    mw = sum(v * materials[c]["molar_mass"] for c, v in x.items())
    total = state["flow"]["value"] / mw
    return {c: v * total for c, v in x.items()}


def test_the_liquid_components_carry_the_crc_liquid_heat_capacities(model):
    materials, _, _ = model
    heat_capacity = pytest.importorskip("chemicals.heat_capacity")
    for c in LIQUID:
        assert materials[c]["liquid_heat_capacity"] == pytest.approx(
            float(heat_capacity.CRC_standard_data.loc[CAS[c], "Cpl"]), abs=0.05
        ), c


def test_the_heat_of_hydrolysis_is_the_crc_liquid_formation_enthalpies(model):
    _, _, reactions = model
    heat = reactions["HYD"]["heat_of_reaction"]
    assert heat["temperature"] == T0
    assert heat["provenance"] == "given"
    heat_capacity = pytest.importorskip("chemicals.heat_capacity")
    hfl = {c: float(heat_capacity.CRC_standard_data.loc[CAS[c], "Hfl"]) for c in LIQUID}
    stoich = reactions["HYD"]["stoichiometry"]
    assert heat["value"] == pytest.approx(sum(n * hfl[c] for c, n in stoich.items()), abs=1.0)


def test_q10_is_the_liquid_conversion_step_duty(model):
    """Reaction heat at 298.15 K plus the liquid streams brought to and from it at their liquid
    heat capacities; at ideal-gas heat capacities the sensible term was -4.17 kW, here -43.6."""
    materials, streams, reactions = model
    s20, s21 = streams["S20"], streams["S21"]
    n_in, n_out = _kmol_h(s20, materials), _kmol_h(s21, materials)
    extent = n_out["FA"] - n_in["FA"]  # kmol/h, HYD is the only reaction of R201
    reaction_kw = extent * reactions["HYD"]["heat_of_reaction"]["value"] / 3600.0
    cp = {c: materials[c]["liquid_heat_capacity"] for c in LIQUID}

    def sensible(n: dict, stream: dict) -> float:
        t = stream["state"]["design"]["temperature"]["value"]
        return sum(v * cp[c] for c, v in n.items()) * (t - T0) / 3600.0

    sensible_kw = sensible(n_out, s21) - sensible(n_in, s20)
    assert sensible_kw == pytest.approx(-43.56, abs=0.05)
    q10 = streams["Q10"]["state"]["design"]["duty"]
    assert q10["provenance"] == "calculated"
    assert q10["source"].startswith("cheme process propagate: conversion duty R201")
    assert q10["value"] == pytest.approx(reaction_kw + sensible_kw, abs=0.01)
    assert q10["value"] == pytest.approx(203.329, abs=0.001)


def test_the_lp_steam_exchange_is_its_streams_and_the_texts_state_it(model):
    _, streams, _ = model
    total = sum(streams[q]["state"]["design"]["duty"]["value"] for q in LPS_STREAMS)
    dataset = _yaml("lca/dataset.yaml")
    lps = next(e for e in dataset["exchanges"] if e["key"] == "feed:LPS")
    assert lps["amount"] == pytest.approx(total, abs=0.01)
    per_kg = total / PRODUCT_KG_H
    assert per_kg == pytest.approx(4.4542, abs=5e-5)
    design = _text("DESIGN.md")
    assert "203.329 kW (calculated)" in design
    assert "27 838.6 kW, 4.4627 to 4.4542 kWh/kg" in design
    assert "4.45 kWh LP steam heat per kg product" in _text("process.yaml")
    assert "LP steam 4.45 kWh" in design


def test_src7_names_the_packages_and_is_not_called_open_data():
    row = next(line for line in (PROCESS / "DESIGN.md").read_text(encoding="utf-8").splitlines()
               if line.startswith("| SRC-7 |"))
    for needle in ("`chemicals` 1.5.2", "`thermo` 0.6.1", "ATCT_G", "CRC_standard_data",
                   "CRC_organic_data", "DIPPR_PERRY_8E", "Poling", "not open data",
                   "ADR 0037", "the handbooks were not read here"):
        assert needle in row, needle
    assert "open data packages" not in row
