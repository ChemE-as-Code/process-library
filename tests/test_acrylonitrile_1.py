"""acrylonitrile-1 (#460): the folder's stated numbers against its own flowsheet.

Fast and without core: the flowsheet's streams (propagated by core) are read as YAML with the
molar masses of process/materials.yaml, and the statements the folder makes in DESIGN.md,
README.md, process.yaml and lca/lca.yaml are checked against them:

- the reactor's selectivities are the source's carbon yields normalised to its conversion, and
  they account for every carbon of the propylene converted;
- the product rate, purity and recovery, the specific consumptions and the co-products per kg;
- the design specifications hold: feed ratios, acid excess, absorber water rate;
- every component separator and mixer closes per component;
- the direct CO2 and its split between reactor and oxidiser;
- the utility lumps are SRC-2's figures scaled by the stated factor;
- the LCI links its three feeds to the library producers and allocates by mass with the stated
  shares; the benchmarks bind the dataset;
- the process is public with CC-BY-4.0, its chemicals are in the registry, and coverage names it.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

KIT = Path(__file__).resolve().parents[1]
PROCESS = KIT / "processes" / "acrylonitrile-1"


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


def kg(streams, mw, sid: str) -> dict[str, float]:
    state = streams[sid]
    comp = state["composition"]
    flow = state["flow"]["value"]
    if comp["basis"] == "mass_fraction":
        return {k: flow * x for k, x in comp["values"].items()}
    assert comp["basis"] == "mole_fraction"
    mm = sum(x * mw[k] for k, x in comp["values"].items())
    return {k: flow * x * mw[k] / mm for k, x in comp["values"].items()}


def kmol(streams, mw, sid: str) -> dict[str, float]:
    return {k: v / mw[k] for k, v in kg(streams, mw, sid).items()}


def test_the_selectivities_are_the_sources_yields_normalised(sheet):
    r101 = next(s for s in sheet["steps"] if s["id"] == "R101")
    sel = r101["selectivity"]
    assert sel["key"] == "C3H6" and sel["conversion"] == 0.975
    yields = {"ACN": 79.7, "MECN": 2.8, "HCN": 1.9, "ACRO": 0.5, "AA": 1.5, "CO": 3.1, "CO2": 8.1}
    carbons = {"ACN": 3, "MECN": 2, "HCN": 1, "ACRO": 3, "AA": 3, "CO": 1, "CO2": 1}
    total = sum(yields.values())
    for product, y in yields.items():
        assert sel["products"][product] == pytest.approx(y / total * 3 / carbons[product], rel=1e-9)
    # every carbon of the propylene converted is in a product
    carbon = sum(sel["products"][p] * carbons[p] / 3 for p in yields)
    assert carbon == pytest.approx(1.0, abs=1e-9)
    # the rest of the ammonia converted (96.5 % of 1.2) beyond the nitriles' nitrogen to N2
    nitriles = (sel["products"]["ACN"] + sel["products"]["HCN"] + sel["products"]["MECN"]) * 0.975
    assert sel["products"]["N2"] == pytest.approx((0.965 * 1.2 - nitriles) / 2 / 0.975, rel=1e-9)


def test_product_rate_purity_recovery_and_consumptions(streams, mw):
    product = kg(streams, mw, "S27")
    total = sum(product.values())
    assert total == pytest.approx(15000, rel=1e-4)
    assert product["ACN"] / total == pytest.approx(0.9975, abs=0.0002)
    made = kg(streams, mw, "S6")["ACN"]
    assert product["ACN"] / made == pytest.approx(0.995, abs=0.001)
    assert streams["S1"]["flow"]["value"] / total == pytest.approx(0.999, abs=0.001)
    assert streams["S2"]["flow"]["value"] / total == pytest.approx(0.485, abs=0.001)
    assert sum(kg(streams, mw, "S25").values()) / total == pytest.approx(0.036, abs=0.001)
    assert sum(kg(streams, mw, "S22").values()) / total == pytest.approx(0.039, abs=0.001)
    liquor = kg(streams, mw, "S10")
    assert sum(liquor.values()) / total == pytest.approx(0.239, abs=0.001)
    assert liquor["AS"] / sum(liquor.values()) == pytest.approx(0.28, abs=0.01)
    assert kg(streams, mw, "S25")["HCN"] / sum(kg(streams, mw, "S25").values()) > 0.995


def test_the_design_specifications_hold(streams, mw):
    c3 = streams["S1"]["flow"]["value"] / mw["C3H6"]
    assert streams["S2"]["flow"]["value"] / mw["NH3"] / c3 == pytest.approx(1.2, rel=1e-4)
    air = kmol(streams, mw, "S3")
    assert sum(air.values()) / c3 == pytest.approx(9.8, rel=1e-4)
    acid = kmol(streams, mw, "S8")["H2SO4"]
    assert acid / kmol(streams, mw, "S6")["NH3"] == pytest.approx(0.525, rel=1e-3)
    assert sum(kmol(streams, mw, "S20").values()) / sum(kmol(streams, mw, "S12").values()) == pytest.approx(4.0, rel=1e-3)


@pytest.mark.parametrize("ins,outs", [
    (["S9"], ["S10", "S11"]),
    (["S12", "S20"], ["S13", "S14"]),
    (["S14"], ["S15", "S16"]),
    (["S16"], ["S17", "S18"]),
    (["S18"], ["S20", "S21"]),
    (["S17"], ["S22", "S23"]),
    (["S15"], ["S25", "S26"]),
    (["S26"], ["S27", "S28"]),
    (["S21", "S23"], ["S24"]),
    (["S13", "S28", "S31", "S32"], ["S33"]),
])
def test_separators_and_mixers_close_per_component(streams, mw, ins, outs):
    def total(ids):
        out: dict[str, float] = {}
        for sid in ids:
            for k, v in kg(streams, mw, sid).items():
                out[k] = out.get(k, 0.0) + v
        return out

    a, b = total(ins), total(outs)
    for comp in set(a) | set(b):
        assert a.get(comp, 0.0) == pytest.approx(b.get(comp, 0.0), abs=1.0 + 0.005 * max(a.get(comp, 0.0), b.get(comp, 0.0)))


def test_direct_co2_and_its_split(streams, mw):
    product = streams["S27"]["flow"]["value"]
    reactor = kg(streams, mw, "S6")["CO2"] / product
    stack = kg(streams, mw, "S34")["CO2"] / product
    assert stack == pytest.approx(0.463, abs=0.001)
    assert reactor == pytest.approx(0.254, abs=0.001)
    assert stack - reactor == pytest.approx(0.209, abs=0.001)
    assert "0.463 kg" in _text("DESIGN.md")


def test_utility_lumps_are_the_scaled_open_design(sheet):
    duty = {s["id"]: s["state"]["design"]["duty"]["value"] for s in sheet["streams"] if s.get("kind") == "energy"}
    factor = 15000 / (272.34 * 53.0634 * 0.999)   # SRC-2: 120 kt/a from 272.34 kmol/h at 99.9 % recovery
    assert factor == pytest.approx(1.039, abs=0.001)
    assert duty["Q7"] == pytest.approx(48.42e3 * factor, rel=1e-3)
    assert duty["Q8"] == pytest.approx((43.15 - 3.39) * 1e3 * factor, rel=1e-3)
    assert duty["Q2"] == pytest.approx(3.39e3 * factor / 4.0, rel=1e-3)
    assert duty["Q4"] == pytest.approx(56.8e3, rel=0.01)
    steam = (duty["Q4"] + duty["Q5"] + duty["Q6"]) / 15000
    assert steam == pytest.approx(4.73, abs=0.01)


def test_lca_links_and_allocation():
    lca = _load("lca/lca.yaml")
    assert lca["functional_unit"]["product"] == "ACNP"
    assert lca["allocation"]["method"] == "mass"
    assert set(lca["allocation"]["coproducts"]) == {"ACNP", "HCNP", "MECNP"}
    mappings = _load("lca/mappings.yaml")["exchanges"]
    assert mappings["feed:C3"]["dataset"]["path"].startswith("processes/propylene-pdh-1/")
    assert mappings["feed:AMM"]["dataset"]["path"] == "processes/ammonia-1/lca/dataset.yaml"
    assert mappings["feed:ACID"]["dataset"]["path"] == "processes/sulfuric-acid-1/lca/dataset.yaml"
    for rel in [m["dataset"]["path"] for m in mappings.values() if "dataset" in m]:
        assert (KIT / rel).is_file()
    dataset = _load("lca/dataset.yaml")
    bench = _load("benchmarks/nitrogen-organics.yaml", KIT)
    entry = next(d for d in bench["datasets"] if d["process"] == "acrylonitrile-1")
    assert entry["dataset"] == dataset["id"]


def test_public_registry_and_coverage():
    manifest = _load("process.yaml")
    assert manifest["publication"] == {"status": "public", "license": "CC-BY-4.0"}
    assert "cheme-as-code>=1.12" in _load("plant.yaml")["requires"]
    registry = {c["slug"] for c in _load("chemicals/chemicals.yaml", KIT)["chemicals"]}
    for flow in manifest["chemistry"]["inputs"] + manifest["chemistry"]["outputs"] + manifest["chemistry"]["utilities"]:
        assert flow["chemical"].split("/")[0] in registry
    coverage = _load("coverage.yaml", KIT)
    item = next(i for i in coverage["entries"] if i.get("id") == "acrylonitrile")
    assert item["rank"] == 52
    assert any(c["process"] == "acrylonitrile-1" for c in item.get("covered_by", []))
