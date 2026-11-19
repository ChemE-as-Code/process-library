"""methyl-methacrylate-1 (#477): the folder's stated numbers against its own flowsheet.

Fast and without core: the flowsheet's streams (propagated by core, duties given by
scripts/mma_balance.py) are read as YAML, and the statements the folder makes in DESIGN.md,
README.md, process.yaml and lca/ are checked against them:

- the MMA yield on ACH is the 91.6 % of US 2023/0416184 A1 Example A2, and the acid and
  methanol ratios are the design specifications' 1.4 and 1.2 mol/mol;
- the spent acid per kg ACH is within 5 % of the patent's Example A2 (2.282 kg/kg);
- the specific consumptions and the tail-gas CO2 and SO2 stated in process.yaml follow from the
  streams; the regenerated acid is 98.5 wt%;
- the rate spec's followers and every cited duty are the script's;
- the Atlas producers the LCI links exist with the named products;
- the process is public with CC-BY-4.0, its chemicals are in the registry, and it is a
  coverage item's covering folder.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest
import yaml

KIT = Path(__file__).resolve().parents[1]
PROCESS = KIT / "processes" / "methyl-methacrylate-1"


def _load(rel: str, root: Path = PROCESS) -> dict:
    return yaml.safe_load((root / rel).read_text(encoding="utf-8"))


def _text(rel: str) -> str:
    return " ".join((PROCESS / rel).read_text(encoding="utf-8").split())


@pytest.fixture(scope="module")
def sheet() -> dict:
    return _load("process/flowsheet.yaml")


@pytest.fixture(scope="module")
def mw() -> dict[str, float]:
    return {c["id"]: c["molar_mass"] for c in _load("process/materials.yaml")["components"]}


@pytest.fixture(scope="module")
def streams(sheet) -> dict[str, dict]:
    return {s["id"]: s["state"]["design"] for s in sheet["streams"] if "state" in s}


@pytest.fixture(scope="module")
def script():
    spec = importlib.util.spec_from_file_location("mma_balance", PROCESS / "scripts" / "mma_balance.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _kmol(streams, mw, sid: str) -> dict[str, float]:
    """Component flows in kmol/h of a material stream (flows are kg/h)."""
    state = streams[sid]
    flow = state["flow"]["value"]
    comp = state["composition"]
    values = comp["values"]
    if comp["basis"] == "mass_fraction":
        return {k: flow * x / mw[k] for k, x in values.items()}
    mean = sum(x * mw[k] for k, x in values.items())
    return {k: flow / mean * x for k, x in values.items()}


def _kg(streams, mw, sid: str) -> dict[str, float]:
    return {k: n * mw[k] for k, n in _kmol(streams, mw, sid).items()}


def test_the_yield_on_ach_is_the_patent_example(streams, mw):
    ach = _kmol(streams, mw, "S3")["ACH"]
    mma = _kmol(streams, mw, "S17")["MMA"]
    assert mma / ach == pytest.approx(0.916, abs=0.0005)
    assert streams["S17"]["flow"]["value"] == pytest.approx(12500, rel=1e-3)
    assert "91.6 %" in _text("DESIGN.md") and "91.6 %" in _text("README.md")


def test_the_acid_and_methanol_ratios_are_the_specs(sheet, streams, mw):
    specs = {s["id"]: s for s in sheet["specs"]}
    assert specs["acid"]["target"]["value"] == 1.4
    assert specs["methanol"]["target"]["value"] == 1.2
    acid = _kmol(streams, mw, "S6")["H2SO4"] / _kmol(streams, mw, "S3")["ACH"]
    meoh = _kmol(streams, mw, "S13")
    assert acid == pytest.approx(1.4, rel=1e-4)
    assert meoh["MEOH"] / meoh["MAM"] == pytest.approx(1.2, rel=1e-4)


def test_the_spent_acid_is_close_to_the_patent_example(streams, mw):
    ach_kg = _kg(streams, mw, "S3")["ACH"]
    spent = streams["S16"]["flow"]["value"] / ach_kg
    assert spent == pytest.approx(2.195, abs=0.002)
    assert abs(spent / (11410 / 5000) - 1) < 0.05
    kg = _kg(streams, mw, "S16")
    total = sum(kg.values())
    assert kg["AHS"] / total == pytest.approx(0.62, abs=0.01)
    assert kg["H2SO4"] / total == pytest.approx(0.21, abs=0.01)


def test_the_stated_consumptions_and_emissions_follow_from_the_streams(streams, mw):
    product = streams["S17"]["flow"]["value"]
    stated = {"S1": 0.634, "S2": 0.295, "S10": 0.327, "S19": 0.228}
    for sid, value in stated.items():
        assert streams[sid]["flow"]["value"] / product == pytest.approx(value, abs=0.0006), sid
    assert streams["S4"]["flow"]["value"] / product * 1000 == pytest.approx(4.6, abs=0.05)
    tail = _kg(streams, mw, "S32")
    assert tail["CO2"] / product == pytest.approx(0.80, abs=0.005)
    assert tail["SO2"] / product * 1000 == pytest.approx(2.9, abs=0.05)
    text = _text("process.yaml")
    for phrase in ("0.634 kg/kg MMA", "0.295 kg/kg MMA", "0.327 kg/kg MMA", "0.228 kg/kg MMA",
                   "0.80 kg per kg MMA", "2.9 g SO2"):
        assert phrase in text, phrase


def test_the_regenerated_acid_is_98_5_wt_percent(streams, mw):
    kg = _kg(streams, mw, "S5")
    assert kg["H2SO4"] / sum(kg.values()) == pytest.approx(0.985, abs=1e-4)


def test_the_followers_and_duties_are_the_script_s(sheet, streams, script, mw):
    b = script.balance()
    rate = next(s for s in sheet["specs"] if s["id"] == "rate")
    follow = rate["vary"]["with"]
    ratios = b["ratios"]
    for sid, key in {"S12": "WATER", "S19": "CH4", "S20": "AIR", "S27": "SECAIR", "S29": "DILW"}.items():
        assert follow[sid] == pytest.approx(ratios[key], abs=2e-6), sid
    # HCN is rounded down so that it never exceeds the acetone (D-004)
    assert ratios["HCN"] - 2e-6 < follow["S2"] <= ratios["HCN"]
    assert streams["S1"]["flow"]["value"] == pytest.approx(b["acetone_kg"], rel=1e-4)
    q = b["q"]
    steam = q["Q3_R301"] + q["Q4_C401_steam"]
    expected = {"Q1": q["Q1_R101"], "Q2": q["Q2_R201"], "Q3": q["Q3_R301"], "Q4": q["Q4_C401_steam"],
                "Q5": q["Q5_C401_cw"], "Q7": q["Q7_C501"], "Q8": q["Q8_R502"],
                "Q9": q["Q6_E501"] - steam, "Q10": q["P_K501"], "Q11": q["P_K502"]}
    for sid, value in expected.items():
        assert streams[sid]["duty"]["value"] == pytest.approx(value, abs=0.11), sid
    assert q["Q6_E501"] > steam, "the waste heat boiler covers the plant's own steam"


def test_the_lci_links_existing_library_producers():
    mappings = _load("lca/mappings.yaml")["exchanges"]
    for key, (path, product) in {
        "feed:ACEF": ("processes/acetone-1/lca/dataset.yaml", "product:ACETONE"),
        "feed:MEOHF": ("processes/methanol-1/lca/dataset.yaml", "product:MEOH"),
        "feed:ACIDF": ("processes/sulfuric-acid-1/lca/dataset.yaml", "product:ACID"),
    }.items():
        assert mappings[key]["dataset"] == {"path": path, "product": product}
        text = (KIT / path).read_text(encoding="utf-8")
        assert f"key: {product}" in text, key
    assert "feed:HCNF" not in mappings, "HCN has no library producer: a gap, never a guess"
    lca = _load("lca/lca.yaml")
    assert lca["functional_unit"]["product"] == "MMAP"
    assert lca["allocation"]["shares"] == {"MMAP": 1.0, "MPSX": 0.0}


def test_the_manifest_registry_and_coverage():
    manifest = _load("process.yaml")
    assert manifest["publication"] == {"status": "public", "license": "CC-BY-4.0"}
    assert manifest["maturity"] == "concept" and manifest["validation"]["status"] == "unreviewed"
    assert _load("plant.yaml")["requires"] == "cheme-as-code>=1.12"
    slugs = {c["slug"] for c in _load("chemicals/chemicals.yaml", KIT)["chemicals"]}
    for side in ("inputs", "outputs", "utilities"):
        for item in manifest["chemistry"][side]:
            assert item["chemical"].split("/")[0] in slugs, item["chemical"]
    items = _load("coverage.yaml", KIT)["entries"]
    item = next(i for i in items if i["id"] == "methyl-methacrylate")
    assert item["chemical"] == "methyl-methacrylate"
    assert [c["process"] for c in item["covered_by"]] == ["methyl-methacrylate-1"]
