"""mdi-1 (#465): the folder's stated numbers against its own flowsheet.

Fast and without core: the flowsheet's streams (propagated by core) are read as YAML, and the
statements the folder makes in DESIGN.md, README.md, process.yaml and lca/lca.yaml are checked
against them:

- the sourced ratios hold on the propagated streams (2.25 mol aniline per mol formaldehyde,
  protonation 0.10, 30 % acid, caustic 1.10 mol per mol HCl, 27.1 % MDA and 35 % phosgene
  solutions, 2.0588 kg phosgene per kg MDA: US 10 640 455 B1, US 10 364 214 B1);
- the MDA is 51.0 wt% two-ring diamines, and R101's selectivities account for the formaldehyde;
- the overall element and mass balance closes over the plant's terminals;
- the stated per-kg consumptions (phosgene 0.784 against the BREF's 0.78, aniline 0.740) and the
  1:4 monomeric to polymeric MDI split follow from the streams;
- the reactions balance by element; every heat stream reaches the LCI;
- the mass allocation's shares are the products' masses;
- the process is public with CC-BY-4.0, the coverage item names it, and every chemical it names
  is in the registry.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

KIT = Path(__file__).resolve().parents[1]
PROCESS = KIT / "processes" / "mdi-1"


def _load(rel: str) -> dict:
    return yaml.safe_load((PROCESS / rel).read_text(encoding="utf-8"))


def _text(rel: str) -> str:
    return " ".join((PROCESS / rel).read_text(encoding="utf-8").split())


@pytest.fixture(scope="module")
def materials() -> dict:
    return _load("process/materials.yaml")


@pytest.fixture(scope="module")
def mw(materials) -> dict[str, float]:
    return {c["id"]: c["molar_mass"] for c in materials["components"]}


@pytest.fixture(scope="module")
def sheet() -> dict:
    return _load("process/flowsheet.yaml")


@pytest.fixture(scope="module")
def streams(sheet) -> dict[str, dict]:
    return {s["id"]: s for s in sheet["streams"]}


def _kg(streams, mw, sid: str) -> dict[str, float]:
    """Component mass flows, kg/h, of a material stream."""
    state = streams[sid]["state"]["design"]
    flow = state["flow"]["value"]
    comp = state["composition"]
    values = comp["values"]
    if comp["basis"] == "mass_fraction":
        return {c: flow * x for c, x in values.items()}
    mean = sum(x * mw[c] for c, x in values.items())
    return {c: flow * x * mw[c] / mean for c, x in values.items()}


def _kmol(streams, mw, sid: str) -> dict[str, float]:
    return {c: m / mw[c] for c, m in _kg(streams, mw, sid).items()}


def _flow(streams, sid: str) -> float:
    return streams[sid]["state"]["design"]["flow"]["value"]


def test_the_sourced_ratios_hold_on_the_streams(streams, mw):
    s5 = _kmol(streams, mw, "S5")
    assert s5["ANL"] / s5["HCHO"] == pytest.approx(2.25, rel=1e-4)
    assert s5["HCL"] / s5["ANL"] == pytest.approx(0.10, rel=1e-4)
    acid = _kg(streams, mw, "S4")
    assert acid["HCL"] / sum(acid.values()) == pytest.approx(0.30, rel=1e-4)
    assert _kmol(streams, mw, "S7")["NAOH"] / _kmol(streams, mw, "S6")["HCL"] == pytest.approx(1.10, rel=1e-4)
    mda = _kg(streams, mw, "S22")
    assert 1 - mda["MCB"] / sum(mda.values()) == pytest.approx(0.271, rel=1e-3)
    phos = _kg(streams, mw, "S25")
    assert phos["COCL2"] / sum(phos.values()) == pytest.approx(0.35, rel=1e-3)
    assert phos["COCL2"] / _flow(streams, "S14") == pytest.approx(2.0588, rel=1e-3)
    # 42 t/h of phosgene per 20.4 t/h of MDA in US 10 364 214 B1
    assert 42.0 / 20.4 == pytest.approx(2.0588, rel=1e-4)


def test_the_mda_is_51_percent_two_ring_and_r101_accounts_for_the_formaldehyde(sheet, streams, mw):
    r101 = next(s for s in sheet["steps"] if s["id"] == "R101")
    sel = r101["selectivity"]["products"]
    # MDA takes 1, PMDA 2 formaldehyde
    assert sel["MDA"] + 2 * sel["PMDA"] == pytest.approx(1.0, abs=1e-9)
    s14 = _kg(streams, mw, "S14")
    assert s14["MDA"] / (s14["MDA"] + s14["PMDA"]) == pytest.approx(0.510, abs=1e-3)


def test_the_reactions_balance_by_element(materials):
    formula = {c["id"]: c["formula"] for c in materials["components"]}

    def atoms(f: str) -> dict[str, int]:
        out: dict[str, int] = {}
        for el, n in re.findall(r"([A-Z][a-z]?)(\d*)", f):
            out[el] = out.get(el, 0) + int(n or 1)
        return out

    for r in _load("process/reactions.yaml")["reactions"]:
        total: dict[str, float] = {}
        for comp, nu in r["stoichiometry"].items():
            for el, n in atoms(formula[comp]).items():
                total[el] = total.get(el, 0) + nu * n
        assert all(abs(v) < 1e-9 for v in total.values()), (r["id"], total)


def test_the_plant_balance_closes(sheet, streams):
    feeds = {f["id"] for f in sheet["feeds"]}
    products = {p["id"] for p in sheet["products"]}
    inflow = outflow = 0.0
    for s in sheet["streams"]:
        if s.get("kind") == "energy":
            continue
        term_from = s["from"].split(".")[0]
        term_to = s["to"].split(".")[0]
        if term_from in feeds:
            inflow += _flow(streams, s["id"])
        if term_to in products:
            outflow += _flow(streams, s["id"])
    assert outflow == pytest.approx(inflow, rel=1e-4)


def test_the_stated_consumptions_and_split_follow_from_the_streams(streams):
    crude = _flow(streams, "S34")
    assert crude == pytest.approx(22197, rel=1e-3)
    assert _flow(streams, "S24") / crude == pytest.approx(0.784, abs=5e-4)
    assert _flow(streams, "S1") / crude == pytest.approx(0.740, abs=5e-4)
    assert _flow(streams, "S36") / crude == pytest.approx(0.20, abs=0.002)
    assert _flow(streams, "S37") / _flow(streams, "S36") == pytest.approx(4.0, rel=0.01)
    text = _text("README.md")
    for stated in ("0.740 kg aniline", "0.784 kg phosgene", "4.44 t/h monomeric MDI", "17.75 t/h polymeric MDI"):
        assert stated in text
    # phosgene-1 supplies the whole fresh phosgene within 0.4 % (DESIGN.md D-005)
    phosgene1 = yaml.safe_load((KIT / "processes" / "phosgene-1" / "process" / "flowsheet.yaml").read_text(encoding="utf-8"))
    s7 = next(s for s in phosgene1["streams"] if s["id"] == "S7")["state"]["design"]["flow"]["value"]
    assert abs(_flow(streams, "S24") / s7 - 1) < 0.004


def test_every_heat_stream_reaches_the_lci(sheet):
    lca = _load("lca/lca.yaml")
    keys = {f["key"] for f in lca["flows"]}
    utilities = {t["id"]: kind for kind, terms in (("feed", sheet["feeds"]), ("product", sheet["products"])) for t in terms if t.get("category") == "utility"}
    used = set()
    for s in sheet["streams"]:
        if s.get("kind") != "energy":
            continue
        for end in (s["from"], s["to"]):
            term = end.split(".")[0]
            if term in utilities:
                used.add(f"{utilities[term]}:{term}")
    assert used and used <= keys


def test_the_mass_allocation_shares_are_the_product_masses(streams):
    lca = _load("lca/lca.yaml")
    assert lca["allocation"]["method"] == "mass"
    products = {"MDIP": "S36", "PMDIP": "S37", "HCLG": "S39"}
    assert set(lca["allocation"]["coproducts"]) == set(products)
    total = sum(_flow(streams, s) for s in products.values())
    shares = {p: _flow(streams, s) / total for p, s in products.items()}
    results = (PROCESS / "lca" / "results.md").read_text(encoding="utf-8")
    for p, share in shares.items():
        assert f"{p} {100 * share:.1f}%" in results


def test_publication_coverage_and_registry():
    meta = _load("process.yaml")
    assert meta["publication"] == {"status": "public", "license": "CC-BY-4.0"}
    assert "cheme-as-code>=1.12" in _load("plant.yaml")["requires"]
    coverage = yaml.safe_load((KIT / "coverage.yaml").read_text(encoding="utf-8"))
    item = next(e for e in coverage["entries"] if e["id"] == "mdi-tdi")
    assert item["rank"] == 53
    assert any(c["process"] == "mdi-1" for c in item.get("covered_by", []))
    registry = yaml.safe_load((KIT / "chemicals" / "chemicals.yaml").read_text(encoding="utf-8"))
    slugs = {c["slug"] for c in registry["chemicals"]}
    named = {e["chemical"].split("/")[0] for part in ("inputs", "outputs", "utilities") for e in meta["chemistry"][part]}
    assert named <= slugs, named - slugs
