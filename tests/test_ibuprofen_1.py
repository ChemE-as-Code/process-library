"""ibuprofen-1 (#508): the folder's stated numbers against its own files.

Fast, without core: reads the flowsheet propagate wrote, the recipe, the reactions and the
manifest, and checks the statements DESIGN.md, process.yaml and README.md make:

- the element balance of the three reaction steps closes on their stoichiometry;
- the design specifications hold in the written streams (ratios, the 25 wt% feed, the capacity);
- the recipe's batch closes the flowsheet's product rate;
- the per-kg figures of process.yaml and the purity and yield DESIGN.md states follow the streams;
- the entry is public with CC-BY-4.0 and its chemicals are in the registry.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

KIT = Path(__file__).resolve().parents[1]
PROCESS = KIT / "processes" / "ibuprofen-1"

MW = {
    "IBB": 134.222, "AC2O": 102.089, "HOAC": 60.052, "HF": 20.006, "IBAP": 176.259,
    "ISO": 176.259, "H2": 2.016, "IBPE": 178.275, "IBPET": 162.276, "CO": 28.01,
    "HCL": 36.458, "H2O": 18.015, "IBU": 206.285, "IBU_S": 206.285, "IPPA": 206.285,
    "HE": 338.535, "HEX": 86.178,
}


def _yaml(rel: str) -> dict:
    return yaml.safe_load((PROCESS / rel).read_text(encoding="utf-8"))


def _text(rel: str) -> str:
    return " ".join((PROCESS / rel).read_text(encoding="utf-8").split())


@pytest.fixture(scope="module")
def streams() -> dict:
    return {s["id"]: s for s in _yaml("process/flowsheet.yaml")["streams"]}


def _mass(stream: dict) -> dict[str, float]:
    st = stream["state"]["design"]
    flow = st["flow"]["value"]
    comp = st["composition"]
    vals = comp["values"]
    if comp["basis"] == "mole_fraction":
        mm = sum(x * MW[k] for k, x in vals.items())
        return {k: flow * x * MW[k] / mm for k, x in vals.items()}
    return {k: flow * x for k, x in vals.items()}


def _duty(streams: dict, sid: str) -> float:
    return streams[sid]["state"]["design"]["duty"]["value"]


def test_materials_cover_the_flowsheet_and_molar_masses() -> None:
    comps = {c["id"]: c for c in _yaml("process/materials.yaml")["components"]}
    assert set(MW) <= set(comps)
    for cid, mm in MW.items():
        assert comps[cid]["molar_mass"] == pytest.approx(mm, abs=1e-3)
    assert comps["IBU_S"]["phase"] == "solid"


def test_reactions_balance_elements() -> None:
    formula = {c["id"]: c["formula"] for c in _yaml("process/materials.yaml")["components"]}

    def atoms(f: str) -> dict[str, int]:
        out: dict[str, int] = {}
        for el, n in re.findall(r"([A-Z][a-z]?)(\d*)", f):
            out[el] = out.get(el, 0) + int(n or 1)
        return out

    for r in _yaml("process/reactions.yaml")["reactions"]:
        tot: dict[str, int] = {}
        for cid, nu in r["stoichiometry"].items():
            for el, n in atoms(formula[cid]).items():
                tot[el] = tot.get(el, 0) + nu * n
        assert all(v == 0 for v in tot.values()), (r["id"], tot)


def test_flowsheet_mass_closes(streams: dict) -> None:
    feeds = ["S1", "S2", "S6", "S13", "S17", "S18", "S25", "S35"]
    outs = ["S33", "S11", "S10", "S47", "S39", "S46"]
    fin = sum(sum(_mass(streams[s]).values()) for s in feeds)
    fout = sum(sum(_mass(streams[s]).values()) for s in outs)
    assert fin == pytest.approx(fout, rel=2e-3)


def test_design_specifications_hold(streams: dict) -> None:
    s3, s4, s5 = _mass(streams["S3"]), _mass(streams["S4"]), _mass(streams["S5"])
    ibb_left = s5["IBB"] / MW["IBB"]
    assert (s4["AC2O"] / MW["AC2O"]) / ibb_left == pytest.approx(2 / 0.15, rel=1e-3)
    assert (s3["HF"] / MW["HF"]) / ibb_left == pytest.approx(49.5 / 0.15, rel=1e-3)
    ibb_in = (s3["IBB"] + s4["IBB"]) / MW["IBB"]
    assert 1 - ibb_left / ibb_in == pytest.approx(0.85, abs=2e-3)
    s19 = _mass(streams["S19"])
    assert (s19["HCL"] / MW["HCL"]) / (s19["IBPE"] / MW["IBPE"]) == pytest.approx(0.75, rel=1e-3)
    s29 = _mass(streams["S29"])
    assert s29["IBU"] / sum(s29.values()) == pytest.approx(0.25, rel=1e-3)
    product = sum(_mass(streams["S33"]).values())
    assert product * 7920 / 1000 == pytest.approx(3500, rel=2e-3)


def test_recipe_closes_the_product_rate(streams: dict) -> None:
    recipe = _yaml("process/recipe.yaml")
    product = sum(_mass(streams["S33"]).values())
    batch = recipe["batch_size"]["value"]
    assert batch == pytest.approx(product * 9.0, rel=1e-3)
    assert recipe["batch_size"]["stream"] == "S33"
    assert recipe["hours_per_year"]["value"] == 7920
    assert "3977" in _text("DESIGN.md") and "880 batches" in _text("DESIGN.md")


def test_stated_purity_yield_and_per_kg(streams: dict) -> None:
    s33 = _mass(streams["S33"])
    product = sum(s33.values())
    purity = (s33["IBU"] + s33["IBU_S"]) / product
    assert purity == pytest.approx(0.9956, abs=5e-4)
    ibb = sum(_mass(streams["S1"]).values())
    yield_ = ((s33["IBU"] + s33["IBU_S"]) / MW["IBU"]) / (ibb / MW["IBB"])
    assert yield_ == pytest.approx(0.670, abs=1e-3)
    assert "99.56 wt%" in _text("DESIGN.md") and "67.0 %" in _text("DESIGN.md")
    per_kg = {"S1": 0.967, "S2": 0.763, "S18": 0.166, "S11": 0.456}
    for sid, value in per_kg.items():
        assert sum(_mass(streams[sid]).values()) / product == pytest.approx(value, abs=1.5e-3)
    steam = sum(_duty(streams, q) for q in ["Q2", "Q3", "Q5", "Q10", "Q13", "Q15"])
    assert steam / product == pytest.approx(3.34, abs=0.01)
    brine = sum(_duty(streams, q) for q in ["Q4", "Q12", "Q14"])
    assert brine / product == pytest.approx(1.63, abs=0.01)


def test_hazard_and_mtt_are_recorded() -> None:
    fs = _yaml("process/flowsheet.yaml")
    r101 = next(s for s in fs["steps"] if s["id"] == "R101")
    assert r101["reactor"] == "semibatch"
    assert r101["hazard"]["mtt"] == 373.15
    assert "MTSR 357.7 K" in _text("DESIGN.md")


def test_public_manifest_and_registry() -> None:
    manifest = _yaml("process.yaml")
    assert manifest["publication"] == {"status": "public", "license": "CC-BY-4.0"}
    slugs = {c["slug"] for c in yaml.safe_load((KIT / "chemicals" / "chemicals.yaml").read_text(encoding="utf-8"))["chemicals"]}
    chem = manifest["chemistry"]
    for group in ("inputs", "outputs", "utilities"):
        for flow in chem[group]:
            assert flow["chemical"] in slugs, flow["chemical"]
    coverage = yaml.safe_load((KIT / "coverage.yaml").read_text(encoding="utf-8"))
    found = [i for i in coverage["entries"] if i.get("id") == "ibuprofen"]
    assert found and found[0]["covered_by"][0]["process"] == "ibuprofen-1"
