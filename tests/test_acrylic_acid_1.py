"""acrylic-acid-1 (#475): the folder's stated numbers against its own flowsheet.

Fast and without core: the flowsheet's streams (propagated by core and given by
scripts/aa_balance.py) are read as YAML, and the statements the folder makes in DESIGN.md,
README.md, process.yaml and lca/lca.yaml are checked against them:

- the feed ratios are those of US 4 873 368 A, Examples 2 and 5 (D-004);
- the first stage's selectivities give Example 2's yields, and both stages Example 5's 87.8 %
  acrylic acid and 0.4 % acrolein on the propylene fed (D-005);
- the specific propylene use and the overall yield stated in README.md and process.yaml follow
  from S1 and S27;
- the absorber's bottoms is 55 wt% acrylic acid, C-401's bottoms 7 wt% toluene with at most
  0.5 wt% water, the product meets its specification (D-007 to D-009);
- every separator's recovery fractions lie in [0, 1] and add up to at most 1 per component;
- the exergy shares of the allocation follow from the properties and the flows (D-012);
- the reactor duties are core's (calculated), the other duties the script's (assumed);
- every heat stream reaches the LCI;
- the process is public with CC-BY-4.0 and requires cheme-as-code 1.12.
"""

from __future__ import annotations

import csv
from pathlib import Path

import pytest
import yaml

KIT = Path(__file__).resolve().parents[1]
PROCESS = KIT / "processes" / "acrylic-acid-1"


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
def mw() -> dict[str, float]:
    return {c["id"]: c["molar_mass"] for c in _load("process/materials.yaml")["components"]}


def _kmol(stream: dict, mw: dict) -> dict[str, float]:
    """Component flows in kmol/h of a stream given in kg/h with mole or mass fractions."""
    comp = stream["composition"]
    z = {k: v for k, v in comp["values"].items() if v}
    flow = stream["flow"]["value"]
    if comp["basis"] == "mole_fraction":
        mean = sum(v * mw[k] for k, v in z.items()) / sum(z.values())
        total = flow / mean
        return {k: v / sum(z.values()) * total for k, v in z.items()}
    return {k: flow * v / mw[k] for k, v in z.items()}


def _mass_fractions(stream: dict, mw: dict) -> dict[str, float]:
    n = _kmol(stream, mw)
    m = {k: v * mw[k] for k, v in n.items()}
    total = sum(m.values())
    return {k: v / total for k, v in m.items()}


def test_feed_ratios_are_the_patents(streams, mw):
    c3 = _kmol(streams["S1"], mw)["C3H6"]
    air = sum(_kmol(streams["S2"], mw).values())
    steam1 = _kmol(streams["S4"], mw)["H2O"]
    steam2 = _kmol(streams["S9"], mw)["H2O"]
    # Example 2: 12 % propylene, 10 % steam, 78 % air; Example 5: 7.5, 15, 77.5 in both stages
    assert steam1 / c3 == pytest.approx(10 / 12, rel=1e-4)
    assert (steam1 + steam2) / c3 == pytest.approx(15 / 7.5, rel=1e-4)
    assert air / c3 == pytest.approx(77.5 / 7.5, rel=1e-4)
    split = next(s for s in _load("process/flowsheet.yaml")["steps"] if s["id"] == "SP101")["split"]["primary"]
    assert split == pytest.approx((78 / 12) / (77.5 / 7.5), rel=1e-6)


def test_reactor_yields_are_the_patents(streams, mw):
    c3_in = _kmol(streams["S5"], mw)["C3H6"]
    s6 = _kmol(streams["S6"], mw)
    s11 = _kmol(streams["S11"], mw)
    # Example 2: conversion 98.5 %, acrolein 80.2 %, acrylic acid 11.7 %
    assert 1 - s6["C3H6"] / c3_in == pytest.approx(0.985, abs=2e-4)
    assert s6["ACR"] / c3_in == pytest.approx(0.802, abs=2e-4)
    assert s6["AA"] / c3_in == pytest.approx(0.117, abs=2e-4)
    # Example 5: 87.8 % acrylic acid, 0.4 % acrolein on the propylene fed
    assert s11["AA"] / c3_in == pytest.approx(0.878, abs=2e-4)
    assert s11["ACR"] / c3_in == pytest.approx(0.004, abs=2e-4)


def test_stated_consumption_and_yield(streams, mw):
    product = streams["S27"]["flow"]["value"]
    assert product == pytest.approx(12500, rel=1e-3)
    spec = streams["S1"]["flow"]["value"] / product
    assert round(spec, 3) == 0.686
    aa = _kmol(streams["S27"], mw)["AA"] / _kmol(streams["S1"], mw)["C3H6"]
    assert round(aa * 100, 1) == 85.6
    for rel in ("README.md", "process.yaml"):
        text = _text(rel)
        assert "0.686 kg" in text and "85.6 %" in text, rel


def test_compositions_meet_the_stated_targets(streams, mw):
    assert _mass_fractions(streams["S15"], mw)["AA"] == pytest.approx(0.55, abs=5e-4)
    s18 = _mass_fractions(streams["S18"], mw)
    assert s18["TOL"] == pytest.approx(0.07, abs=5e-4)
    assert s18.get("H2O", 0) <= 0.005
    product = _mass_fractions(streams["S27"], mw)
    assert product["AA"] >= 0.995
    assert product.get("HAC", 0) <= 0.001 and product.get("H2O", 0) <= 0.001
    assert product["MEHQ"] == pytest.approx(200e-6, rel=0.01)


def test_recovery_fractions_are_shares(sheet):
    for step in sheet["steps"]:
        rec = step.get("recovery")
        if not rec:
            continue
        totals: dict[str, float] = {}
        for comps in rec["outlets"].values():
            for comp, share in comps.items():
                assert 0 <= share <= 1, (step["id"], comp)
                totals[comp] = totals.get(comp, 0) + share
        assert all(v <= 1 + 1e-12 for v in totals.values()), step["id"]


def test_exergy_shares(sheet, streams):
    lca = _load("lca/lca.yaml")
    props = lca["allocation"]["properties"]
    duties = {s["id"]: s["state"]["design"]["duty"]["value"] for s in sheet["streams"] if s.get("kind") == "energy"}
    acid = props["PRODUCT"]["exergy"] * streams["S27"]["flow"]["value"]
    steam = props["STMX"]["exergy"] * (duties["Q2"] + duties["Q3"])
    share = acid / (acid + steam)
    assert round(share * 100, 1) == 83.6
    assert "83.6 %" in _text("README.md") and "83.6 %" in _text("DESIGN.md")


def test_duty_provenance(sheet):
    energy = {s["id"]: s["state"]["design"]["duty"] for s in sheet["streams"] if s.get("kind") == "energy"}
    for qid in ("Q2", "Q3"):
        assert energy[qid]["provenance"] == "calculated", qid
    for qid in ("Q1", "Q4", "Q5", "Q6", "Q7", "Q8", "Q9", "Q10", "Q11"):
        assert energy[qid]["provenance"] == "assumed" and energy[qid]["source"].startswith("scripts/aa_balance.py"), qid


def test_every_heat_stream_reaches_the_lci(sheet):
    with (PROCESS / "lca" / "inventory.csv").open(encoding="utf-8") as fh:
        cited = " ".join(row["streams"] for row in csv.DictReader(fh))
    for s in sheet["streams"]:
        if s.get("kind") == "energy":
            assert s["id"] in cited.split(), s["id"]


def test_published_public_with_cc_by():
    publication = _load("process.yaml")["publication"]
    assert publication == {"status": "public", "license": "CC-BY-4.0"}


def test_requires_core_1_12():
    assert _load("plant.yaml")["requires"] == "cheme-as-code>=1.12"
