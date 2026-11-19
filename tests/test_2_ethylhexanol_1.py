"""2-ethylhexanol-1 (#511): the folder's stated numbers against its own flowsheet.

Fast and without core: the flowsheet's streams (propagated by core, the duties given by
scripts/balance.py) are read as YAML, and the statements the folder makes in DESIGN.md,
README.md, process.yaml and lca/ are checked against them:

- the crude, the isobutanal and the n-butanal meet the compositions of US 4 684 750 A, the
  aldol's organic phase holds more than 93 wt% 2-ethylhexenal and its aqueous phase 1-2 wt%
  NaOH, and the yield on n-butanal is the patent's 97.74 % of theory;
- every reaction balances its elements and its heat of reaction follows from the formation
  enthalpies scripts/balance.py uses;
- the separators' outlets close on their inlets per component;
- R-101's heat goes to C-102's reboiler, which R-301's steam completes; DESIGN.md's duty table
  matches the energy streams;
- the specific consumptions stated in process.yaml follow from the streams, the feeds are linked
  to their library producers, and the process is public with CC-BY-4.0.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

KIT = Path(__file__).resolve().parents[1]
PROCESS = KIT / "processes" / "2-ethylhexanol-1"


def _load(rel: str) -> dict:
    return yaml.safe_load((PROCESS / rel).read_text(encoding="utf-8"))


def _text(rel: str) -> str:
    return " ".join((PROCESS / rel).read_text(encoding="utf-8").split())


@pytest.fixture(scope="module")
def sheet() -> dict:
    return _load("process/flowsheet.yaml")


@pytest.fixture(scope="module")
def comps() -> dict[str, dict]:
    return {c["id"]: c for c in _load("process/materials.yaml")["components"]}


@pytest.fixture(scope="module")
def streams(sheet) -> dict[str, dict]:
    return {s["id"]: s["state"]["design"] for s in sheet["streams"] if s.get("kind") != "energy"}


@pytest.fixture(scope="module")
def duties(sheet) -> dict[str, float]:
    return {s["id"]: s["state"]["design"]["duty"]["value"] for s in sheet["streams"]
            if s.get("kind") == "energy"}


def _kg(state: dict, comps) -> dict[str, float]:
    comp = state["composition"]
    x = comp["values"]
    flow = state["flow"]["value"]
    if comp["basis"] == "mole_fraction":
        mw = sum(x[c] * comps[c]["molar_mass"] for c in x)
        return {c: flow / mw * x[c] * comps[c]["molar_mass"] for c in x if x[c] > 0}
    return {c: flow * x[c] for c in x if x[c] > 0}


def _wt(state, comps) -> dict[str, float]:
    kg = _kg(state, comps)
    total = sum(kg.values())
    return {c: v / total for c, v in kg.items()}


def test_public_and_core_version():
    manifest = _load("process.yaml")
    assert manifest["publication"] == {"status": "public", "license": "CC-BY-4.0"}
    assert manifest["maturity"] == "concept"
    assert _load("plant.yaml")["requires"] == "cheme-as-code>=1.13"


def test_compositions_of_the_patent(streams, comps):
    crude = _wt(streams["S13"], comps)
    aldehydes = crude["NBAL"] + crude["IBAL"] + crude["BUBU"]
    assert crude["IBAL"] / aldehydes == pytest.approx(0.050, abs=0.002)
    assert crude["BUBU"] / aldehydes == pytest.approx(0.010, abs=0.001)
    iso = _wt(streams["S15"], comps)
    assert iso["IBAL"] == pytest.approx(0.999, abs=0.0005)
    nbal = _wt(streams["S17"], comps)
    assert nbal["IBAL"] == pytest.approx(0.002, abs=0.0005)
    assert nbal["NBAL"] == pytest.approx(0.988, abs=0.002)
    organic = _wt(streams["S25"], comps)
    assert organic["EPA"] > 0.93
    caustic = _wt(streams["S23"], comps)
    assert 0.01 <= caustic["NAOH"] <= 0.02
    product = _wt(streams["S46"], comps)
    assert product["EH"] > 0.999


def test_yield_on_n_butanal(streams, comps):
    eh = _kg(streams["S46"], comps)["EH"] / comps["EH"]["molar_mass"]
    nbal = _kg(streams["S17"], comps)["NBAL"] / comps["NBAL"]["molar_mass"]
    assert eh / (nbal / 2) == pytest.approx(0.9774, abs=0.001)
    assert sum(_kg(streams["S46"], comps).values()) == pytest.approx(15000, rel=0.001)


def _atoms(formula: str) -> dict[str, int]:
    out: dict[str, int] = {}
    for el, n in re.findall(r"([A-Z][a-z]?)(\d*)", formula):
        out[el] = out.get(el, 0) + (int(n) if n else 1)
    return out


def test_reactions_balance_and_heats(comps):
    hf = {"C3H6": 20370.0, "C3H8": -104390.0, "CO": -110525.0, "H2": 0.0, "NBAL": -239200.0,
          "IBAL": -247300.0, "H2O": -285825.0, "EPA": -261300.0, "EH": -432800.0,
          "NBOL": -327300.0, "IBOL": -334700.0, "BUBU": -573290.0}
    for r in _load("process/reactions.yaml")["reactions"]:
        change: dict[str, float] = {}
        for c, nu in r["stoichiometry"].items():
            for el, n in _atoms(comps[c]["formula"]).items():
                change[el] = change.get(el, 0) + nu * n
        assert all(abs(v) < 1e-9 for v in change.values()), r["id"]
        dh = sum(nu * hf[c] for c, nu in r["stoichiometry"].items())
        assert r["heat_of_reaction"]["value"] == pytest.approx(dh, abs=1.0), r["id"]


def test_separators_close(sheet, streams, comps):
    for step in sheet["steps"]:
        if "recovery" not in step:
            continue
        ins = [s for s in sheet["streams"] if s.get("kind") != "energy"
               and s["to"].split(".")[0] == step["id"]]
        outs = [s for s in sheet["streams"] if s.get("kind") != "energy"
                and s["from"].split(".")[0] == step["id"]]
        total_in: dict[str, float] = {}
        for s in ins:
            for c, v in _kg(streams[s["id"]], comps).items():
                total_in[c] = total_in.get(c, 0) + v
        total_out: dict[str, float] = {}
        for s in outs:
            for c, v in _kg(streams[s["id"]], comps).items():
                total_out[c] = total_out.get(c, 0) + v
        for c in set(total_in) | set(total_out):
            assert total_out.get(c, 0) == pytest.approx(total_in.get(c, 0), rel=1e-3, abs=0.05), (step["id"], c)


def test_reactor_heat_to_c102(duties):
    # R-101's heat goes to C-102's reboiler, R-301's LP steam completes it; R-301's steam serves
    # C-102, R-302 and the export
    assert duties["Q1"] + duties["Q17"] + duties["Q2"] == pytest.approx(11088.4, abs=0.2)
    assert duties["Q2"] + duties["Q3"] + duties["Q4"] == pytest.approx(4906.5, abs=0.2)
    design = _text("DESIGN.md")
    for q in ("Q2", "Q3", "Q4", "Q5", "Q8", "Q9", "Q12", "Q13"):
        assert f"{duties[q]:.1f}" in design, q
    assert f"{duties['Q1']:.1f} + {duties['Q17']:.1f}" in design


def test_specific_consumptions(streams, comps, duties):
    eh = sum(_kg(streams["S46"], comps).values())
    per = {s: sum(_kg(streams[s], comps).values()) / eh for s in ("S1", "S2", "S35", "S15")}
    desc = _text("process.yaml")
    assert f"{per['S1']:.3f} kg propylene" in desc
    assert f"{per['S2']:.3f} kg synthesis gas" in desc
    assert f"{per['S35']:.3f} kg hydrogen" in desc
    assert f"{per['S15']:.3f} kg isobutanal" in desc
    mps = (duties["Q8"] + duties["Q10"] + duties["Q12"] + duties["Q15"]) / eh
    assert f"{mps:.3f} kWh" in desc or f"{mps:.2f} kWh" in desc


def test_lci_links():
    mappings = _load("lca/mappings.yaml")["exchanges"]
    assert "propylene-pdh-1" in mappings["feed:C3"]["dataset"]["path"]
    assert "hydrogen-1" in mappings["feed:H2F"]["dataset"]["path"]
    assert "chlor-alkali-1" in mappings["feed:NAOH"]["dataset"]["path"]
    lca = _load("lca/lca.yaml")
    shares = lca["allocation"]["shares"]
    assert sum(shares.values()) == pytest.approx(1.0)
    assert shares["LPSX"] == 0.0
