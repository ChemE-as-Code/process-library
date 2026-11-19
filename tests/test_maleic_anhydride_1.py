"""maleic-anhydride-1 (#478): the folder's stated numbers against its own flowsheet.

Fast and without core: the flowsheet's streams (propagated by core and given by
scripts/balance.py) are read as YAML, and the statements the folder makes in DESIGN.md,
README.md, process.yaml and lca/lca.yaml are checked against them:

- the reactor's conversions are the overall conversion times the selectivities of US 7 589 217
  B2, and the reactor gas follows from them;
- the specific consumptions and the overall yield follow from the feeds and the product;
- the reactor feed is SRC-1's (1.8 mol% butane, 1.7 mol% water) and the air ratio the script's;
- the absorber's off-gas shares are SRC-2's, the lean solvent's MA about 0.3 wt%, the
  circulation 4.8 kg per kg of MA in the gas, the overall recovery within SRC-2's 98.5 to 99 %;
- the product meets the stated specification;
- the heats of reaction follow from the formation enthalpies of materials.yaml, the
  flowsheet's script values are the script's, and the steam and power totals per kg are the
  stated ones;
- the feed is above butane's lower flammable limit, as DESIGN.md D-011 says;
- every energy stream reaches the LCI, the steam export carries share 0;
- the registry has the slugs process.yaml names; the process is public with CC-BY-4.0 and
  requires cheme-as-code 1.12.
"""

from __future__ import annotations

import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

KIT = Path(__file__).resolve().parents[1]
PROCESS = KIT / "processes" / "maleic-anhydride-1"


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
def materials() -> dict[str, dict]:
    return {c["id"]: c for c in _load("process/materials.yaml")["components"]}


@pytest.fixture(scope="module")
def reactions() -> dict[str, dict]:
    return {r["id"]: r for r in _load("process/reactions.yaml")["reactions"]}


def _kg(streams: dict, materials: dict, sid: str) -> dict[str, float]:
    state = streams[sid]
    flow = float(state["flow"]["value"])
    comp = state["composition"]
    x = {k: float(v) for k, v in comp["values"].items()}
    if comp["basis"] == "mole_fraction":
        mass = {k: v * materials[k]["molar_mass"] for k, v in x.items()}
        total = sum(mass.values())
        x = {k: v / total for k, v in mass.items()}
    return {k: flow * v for k, v in x.items()}


def _kmol(streams, materials, sid) -> dict[str, float]:
    return {k: v / materials[k]["molar_mass"] for k, v in _kg(streams, materials, sid).items()}


def _duty(streams, sid: str) -> float:
    return float(streams[sid]["duty"]["value"])


def test_reactor_conversions_are_conversion_times_selectivity(reactions):
    x = 0.81
    sel = {"MAF": 0.695, "COF": 0.174, "CO2F": 0.106, "AAF": 0.015, "ACRF": 0.010}
    assert sum(sel.values()) == pytest.approx(1.0)
    for rid, s in sel.items():
        assert reactions[rid]["conversion"]["key"] == "NC4"
        assert reactions[rid]["conversion"]["value"] == pytest.approx(x * s, abs=1e-6)
    # CO : CO2 on carbon after SRC-5's 18.1 and 11.1 %
    assert sel["COF"] / (sel["COF"] + sel["CO2F"]) == pytest.approx(18.1 / 29.2, abs=0.005)


def test_reactor_gas_follows_the_conversions(streams, materials):
    n5, n6 = _kmol(streams, materials, "S5"), _kmol(streams, materials, "S6")
    assert 1 - n6["NC4"] / n5["NC4"] == pytest.approx(0.81, abs=1e-4)
    assert n6["MA"] / (n5["NC4"] - n6["NC4"]) == pytest.approx(0.695, abs=1e-4)


def test_heats_of_reaction_from_formation_enthalpies(reactions, materials):
    for r in reactions.values():
        dh = sum(v * materials[k]["ideal_gas"]["dHf_298"] for k, v in r["stoichiometry"].items())
        assert r["heat_of_reaction"]["value"] == pytest.approx(dh, abs=1.0), r["id"]
    # SRC-4: about -1236 kJ/mol for the main reaction
    assert reactions["MAF"]["heat_of_reaction"]["value"] / 1000 == pytest.approx(-1236, abs=10)


def test_reactions_balance_elements(reactions, materials):
    def atoms(formula: str) -> dict[str, int]:
        out: dict[str, int] = {}
        for el, n in re.findall(r"([A-Z][a-z]?)(\d*)", formula):
            out[el] = out.get(el, 0) + int(n or 1)
        return out

    for r in reactions.values():
        total: dict[str, float] = {}
        for k, v in r["stoichiometry"].items():
            for el, n in atoms(materials[k]["formula"]).items():
                total[el] = total.get(el, 0.0) + v * n
        assert all(abs(v) < 1e-9 for v in total.values()), r["id"]


def test_reactor_feed_is_src1s(streams, materials):
    n5 = _kmol(streams, materials, "S5")
    total = sum(n5.values())
    assert n5["NC4"] / total == pytest.approx(0.018, abs=2e-5)
    assert n5["H2O"] / total == pytest.approx(0.017, abs=2e-5)
    assert float(streams["S5"]["pressure"]["value"]) == pytest.approx(239.0)
    s1, s3 = _kg(streams, materials, "S1"), _kg(streams, materials, "S3")
    assert sum(s3.values()) / sum(s1.values()) == pytest.approx(27.0054, rel=1e-5)


def test_consumptions_and_yield_as_stated(streams, materials):
    product = sum(_kg(streams, materials, "S18").values())
    butane = sum(_kg(streams, materials, "S1").values())
    assert product * 8000 / 1000 == pytest.approx(25000, rel=1e-5)
    assert butane / product == pytest.approx(1.068, abs=0.0005)
    ma = _kg(streams, materials, "S18")["MA"] / materials["MA"]["molar_mass"]
    assert ma / (butane / materials["NC4"]["molar_mass"]) == pytest.approx(0.555, abs=0.0005)
    solvent = sum(_kg(streams, materials, "S15").values())
    assert solvent / product * 1000 == pytest.approx(5.45, abs=0.01)
    co2 = _kg(streams, materials, "S22")["CO2"]
    assert co2 / product == pytest.approx(1.451, abs=0.0005)
    for rel in ("process.yaml", "README.md", "DESIGN.md"):
        text = _text(rel)
        assert "1.068" in text, rel
        assert "1.451" in text or "1.45 kg" in text, rel


def test_absorber_and_recovery_as_src2(sheet, streams, materials):
    a301 = next(s for s in sheet["steps"] if s["id"] == "A301")
    off = a301["recovery"]["outlets"]["offgas"]
    assert 1 - off["MA"] == pytest.approx(0.994)
    assert 1 - off["H2O"] == pytest.approx(0.006)
    assert 1 - off["AA"] == pytest.approx(0.10)
    assert 1 - off["ACR"] == pytest.approx(0.53)
    lean = _kg(streams, materials, "S17")
    assert lean["MA"] / sum(lean.values()) == pytest.approx(0.003, abs=0.0005)
    ratio = _kg(streams, materials, "S16")["DBP"] / _kg(streams, materials, "S7")["MA"]
    assert ratio == pytest.approx(4.8, rel=1e-4)
    # SRC-2's example: 2200 kg per 18 000 m3 at 915 torr and 150 C with 0.75 mol% MA
    n_gas = 915 / 760 * 101.325 * 18000 / (8.314462618 * 423.15)
    assert 2200 / (n_gas * 0.0075 * materials["MA"]["molar_mass"]) == pytest.approx(4.8, abs=0.05)
    recovery = _kg(streams, materials, "S18")["MA"] / _kg(streams, materials, "S6")["MA"]
    assert 0.985 <= recovery <= 0.99


def test_product_meets_specification(streams, materials):
    p = _kg(streams, materials, "S18")
    assert p["MA"] / sum(p.values()) >= 0.995


def test_feed_is_above_the_lower_flammable_limit(streams, materials):
    n5 = _kmol(streams, materials, "S5")
    assert n5["NC4"] / sum(n5.values()) > 0.014  # LFL of butane, IEC 60079-20-1 via chemicals
    assert "above butane's lower flammable limit" in _text("DESIGN.md")


def test_script_values_in_the_flowsheet(sheet, tmp_path):
    out = tmp_path / "balance.json"
    env = dict(os.environ, BALANCE_OUTPUT=str(out))
    pytest.importorskip("thermo")
    subprocess.run([sys.executable, str(PROCESS / "scripts" / "balance.py")], check=True, env=env,
                   cwd=PROCESS, capture_output=True)
    emitted = json.loads(out.read_text())["cases"]["design"]
    by_id = {s["id"]: s for s in sheet["streams"]}
    for sid, values in emitted.items():
        state = by_id[sid]["state"]["design"]
        for q, v in values.items():
            assert state[q]["value"] == pytest.approx(v, abs=0.06), (sid, q)
            assert state[q]["source"].startswith("scripts/balance.py"), (sid, q)


def test_energy_totals_as_stated(streams):
    product = 3125.0
    raised = _duty(streams, "Q2") + _duty(streams, "Q3") + _duty(streams, "Q9")
    drawn = _duty(streams, "Q4") + _duty(streams, "Q7")
    power = sum(_duty(streams, k) for k in ("P1", "P2", "P3", "P4"))
    cw = sum(_duty(streams, k) for k in ("Q5", "Q6", "Q8"))
    assert raised / product == pytest.approx(8.46, abs=0.005)
    assert drawn / product == pytest.approx(1.072, abs=0.001)
    assert power / product == pytest.approx(1.067, abs=0.001)
    assert cw / product == pytest.approx(1.190, abs=0.001)
    for sid in ("Q2", "Q9"):  # core's conversion steps write these (ADR 0059)
        assert streams[sid]["duty"]["provenance"] == "calculated"
        assert streams[sid]["duty"]["source"].startswith("cheme process propagate: conversion duty")


def test_every_energy_stream_reaches_the_lci(sheet):
    lca = _load("lca/lca.yaml")
    keys = {f["key"] for f in lca["flows"]}
    terminals = {t["id"]: kind for kind in ("feeds", "products") for t in sheet[kind]}
    for s in sheet["streams"]:
        if s.get("kind") != "energy":
            continue
        for end in (s["from"], s["to"]):
            node = end.split(".")[0]
            if node in terminals and node != "HPS":
                prefix = "feed" if terminals[node] == "feeds" else "product"
                assert f"{prefix}:{node}" in keys, s["id"]
    assert lca["allocation"]["shares"] == {"MAP": 1.0, "HPS": 0.0}


def test_registry_and_publication():
    manifest = _load("process.yaml")
    registry = yaml.safe_load((KIT / "chemicals" / "chemicals.yaml").read_text(encoding="utf-8"))
    slugs = {c["slug"] for c in registry["chemicals"]}
    for flow in [*manifest["chemistry"]["inputs"], *manifest["chemistry"]["outputs"],
                 *manifest["chemistry"]["utilities"]]:
        assert flow["chemical"].split("/")[0] in slugs, flow["chemical"]
    assert manifest["publication"] == {"status": "public", "license": "CC-BY-4.0"}
    assert "cheme-as-code>=1.12" in (PROCESS / "plant.yaml").read_text(encoding="utf-8")
