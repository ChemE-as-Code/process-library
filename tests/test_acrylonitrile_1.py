"""acrylonitrile-1 (#460): the folder's stated numbers against its own flowsheet.

Fast and without core: the flowsheet's streams (propagated by core) are read as YAML with the
molar masses and ideal-gas heat capacities of process/materials.yaml, and the numbers DESIGN.md,
README.md, process.yaml and lca/lca.yaml state are parsed from their text and checked against
the streams:

- the reactor's selectivities are the source's carbon yields normalised to its conversion, and
  they account for every carbon of the propylene converted;
- the product rate, purity and recovery, and the specific consumptions and co-products per kg as
  DESIGN.md D-011, README.md and process.yaml's chemistry notes state them;
- the design specifications hold: feed ratios, acid excess, absorber water rate;
- every component separator and mixer closes per component;
- the direct CO2 and its split between reactor and oxidiser, as D-011 states it;
- the utilities per kg as D-011 and README.md state them; the LP steam is SRC-2's hot utility
  less its feed preheat, both read from D-009, scaled by the factor D-009 states, which is
  SRC-2's capacity (section 3.1); the chiller is sized on S20; the reaction heat with the feed
  at the reactor temperature is the figure D-004 and README.md state;
- the LCI allocates by mass with the shares D-011 states, links its three feeds to the library
  producers, leaves the exported steam unmapped, and covers the oxidiser with a combustion
  exclusion; the benchmarks bind the dataset;
- the process is public with CC-BY-4.0, its chemicals are in the registry, and coverage names it.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

KIT = Path(__file__).resolve().parents[1]
PROCESS = KIT / "processes" / "acrylonitrile-1"


def _load(rel: str, root: Path = PROCESS) -> dict:
    return yaml.safe_load((root / rel).read_text(encoding="utf-8"))


def _text(rel: str) -> str:
    return " ".join((PROCESS / rel).read_text(encoding="utf-8").split())


def _number(rel: str, pattern: str) -> float:
    """The number the regex *pattern* (one group) finds in a file's text."""
    found = re.search(pattern, _text(rel))
    assert found, f"{rel}: no match for {pattern!r}"
    return float(found.group(1).replace(" ", ""))


def _stated(value: float, rel: str, pattern: str, label: str = "") -> None:
    """*value* rounds to the number *pattern* finds in *rel*, to the digits stated there."""
    found = re.search(pattern, _text(rel))
    assert found, f"{rel}: no match for {pattern!r}"
    text = found.group(1).replace(" ", "")
    decimals = len(text.split(".")[1]) if "." in text else 0
    assert value == pytest.approx(float(text), abs=0.5 * 10**-decimals + 1e-9), f"{label or pattern}: {value} against {text} in {rel}"


R = 8.314462618  # kJ/(kmol K)


def _sensible(streams, mw, comps, sid: str, t1: float, t2: float) -> float:
    """kW to take stream *sid* from t1 to t2, ideal gas (Simpson on the Cp/R polynomials)."""
    total = 0.0
    for k, n in kmol(streams, mw, sid).items():
        if n <= 0:
            continue
        a = comps[k]["ideal_gas"]["cp_R"]
        steps = 100
        h = (t2 - t1) / steps
        f = [sum(c * (t1 + i * h) ** j for j, c in enumerate(a)) for i in range(steps + 1)]
        total += n * R * h / 3 * (f[0] + f[-1] + 4 * sum(f[1:-1:2]) + 2 * sum(f[2:-1:2]))
    return total / 3600.0


@pytest.fixture(scope="module")
def sheet() -> dict:
    return _load("process/flowsheet.yaml")


@pytest.fixture(scope="module")
def mw() -> dict[str, float]:
    return {c["id"]: c["molar_mass"] for c in _load("process/materials.yaml")["components"]}


@pytest.fixture(scope="module")
def comps() -> dict[str, dict]:
    return {c["id"]: c for c in _load("process/materials.yaml")["components"]}


@pytest.fixture(scope="module")
def duty(sheet) -> dict[str, float]:
    return {s["id"]: s["state"]["design"]["duty"]["value"] for s in sheet["streams"] if s.get("kind") == "energy"}


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
    per_kg = {
        "propylene": streams["S1"]["flow"]["value"] / total,
        "ammonia": streams["S2"]["flow"]["value"] / total,
        "sulfuric acid": streams["S8"]["flow"]["value"] / total,
        "natural gas": streams["S32"]["flow"]["value"] / total,
        "quench liquor": sum(kg(streams, mw, "S10").values()) / total,
        "wastewater": sum(kg(streams, mw, "S24").values()) / total,
    }
    for name, value in per_kg.items():  # DESIGN.md D-011
        _stated(value, "DESIGN.md", rf"Per kg of product, unallocated:.*?{name} ([0-9.]+) kg", name)
    hcn = sum(kg(streams, mw, "S25").values()) / total
    mecn = sum(kg(streams, mw, "S22").values()) / total
    liquor = kg(streams, mw, "S10")
    _stated(hcn, "README.md", r"Co-products per kg: HCN ([0-9.]+) kg")
    _stated(mecn, "README.md", r"acetonitrile ([0-9.]+) kg, quench liquor")
    _stated(per_kg["quench liquor"], "README.md", r"quench liquor ([0-9.]+) kg \(about")
    _stated(liquor["AS"] / sum(liquor.values()) * 100, "README.md", r"about ([0-9]+) wt% ammonium sulfate")
    _stated(per_kg["propylene"], "README.md", r"It gives ([0-9.]+) kg propylene")
    _stated(per_kg["ammonia"], "README.md", r"propylene and ([0-9.]+) kg ammonia per kg")
    notes = {f["inventory_key"]: f.get("note", "") for f in _load("process.yaml")["chemistry"]["inputs"] + _load("process.yaml")["chemistry"]["outputs"] if f.get("inventory_key")}
    for key, value in {"feed:C3": per_kg["propylene"], "feed:AMM": per_kg["ammonia"], "product:HCNP": hcn, "product:MECNP": mecn}.items():
        stated = re.match(r"([0-9.]+) kg/kg", notes[key]).group(1)
        assert value == pytest.approx(float(stated), abs=0.5 * 10 ** -len(stated.split(".")[1])), key
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
    _stated(stack, "DESIGN.md", r"fossil CO2 ([0-9.]+) kg \(reactor")
    _stated(reactor, "DESIGN.md", r"fossil CO2 [0-9.]+ kg \(reactor ([0-9.]+),")
    _stated(stack - reactor, "DESIGN.md", r"fossil CO2 [0-9.]+ kg \(reactor [0-9.]+, oxidiser ([0-9.]+),")
    _stated(stack, "README.md", r"Fossil CO2 ([0-9.]+) kg/kg")
    note = next(f["note"] for f in _load("process.yaml")["chemistry"]["outputs"] if f.get("inventory_key") == "product:STACK")
    assert stack == pytest.approx(float(re.search(r"([0-9.]+) kg/kg", note).group(1)), abs=0.005)


def test_utility_lumps_and_their_basis(streams, duty):
    product = streams["S27"]["flow"]["value"]
    design = _text("DESIGN.md")
    # the scale factor D-009 states is SRC-2's capacity: 272.34 kmol/h acrylonitrile at 99.9 %
    # recovery (SRC-2 row of the source register), 53.0634 kg/kmol
    scale = re.search(r"scaled by ([0-9 ]+)/([0-9 ]+),", design)
    assert scale
    src2_rate = _number("DESIGN.md", r"\| SRC-2 \|.*?99\.9 % recovery, ([0-9.]+) kmol/h acrylonitrile") * 53.0634 * 0.999
    assert float(scale.group(2).replace(" ", "")) == pytest.approx(src2_rate, abs=1.0)
    factor = 15000.0 / src2_rate
    hot = _number("DESIGN.md", r"base-case hot utility, ([0-9.]+) MW")
    preheat = re.search(r"5\.28 \+ 9\.71 MW to 420 C and 1\.40 MW to 440 C \(section 4\.2\.3\), ([0-9.]+) MW", design)
    assert preheat and float(preheat.group(1)) == pytest.approx(5.28 + 9.71 + 1.40, abs=1e-9)
    assert duty["Q7"] == pytest.approx((hot - float(preheat.group(1))) * 1e3 * factor, rel=1e-4)
    cold, refrigeration = (float(x) for x in re.search(r"Cooling water: \(([0-9.]+) - ([0-9.]+)\) MW of SRC-2", design).groups())
    # the chiller: S20 from the cooling water's return temperature, liquid water cp (thermo), COP
    s20 = streams["S20"]
    cop = _number("DESIGN.md", r"Refrigeration:.*?electric COP of ([0-9.]+)")
    q_ref = s20["flow"]["value"] * 4.18666 * (308.15 - s20["temperature"]["value"]) / 3600.0
    assert duty["Q2"] == pytest.approx(q_ref / cop, rel=1e-4)
    _stated(q_ref / 1e3, "DESIGN.md", r"to 278 K: ([0-9.]+) MW")
    _stated(duty["Q2"] / 1e3, "DESIGN.md", r"electric COP of [0-9.]+ \(ASSUMED\): ([0-9.]+) MW")
    _stated(duty["Q7"] / 1e3, "DESIGN.md", r"scaled by [0-9 ]+/[0-9 ]+, ([0-9.]+) MW")
    assert duty["Q8"] == pytest.approx((cold - refrigeration) * 1e3 * factor + q_ref * (1 + 1 / cop), rel=1e-4)
    per_kg = {
        "electricity": (duty["Q1"] + duty["Q2"] + duty["Q3"]) / product,
        "LP steam": duty["Q7"] / product,
        "cooling": duty["Q8"] / product,
        "HP steam export": (duty["Q4"] + duty["Q5"] + duty["Q6"]) / product,
    }
    for name, value in per_kg.items():  # DESIGN.md D-011
        _stated(value, "DESIGN.md", rf"Per kg of product, unallocated:.*?{name} ([0-9.]+) kWh", name)
    _stated(per_kg["electricity"], "README.md", r"power ([0-9.]+) kWh per kg")
    _stated(per_kg["LP steam"], "README.md", r"LP steam ([0-9.]+) kWh per kg")
    _stated(per_kg["cooling"], "README.md", r"cooling water ([0-9.]+) kWh per kg")
    _stated(per_kg["HP steam export"], "README.md", r"HP steam raised ([0-9.]+) kWh per kg")


def test_reaction_heat_on_the_sources_basis(streams, mw, comps, duty):
    """Q4 is net of heating S5 in the bed; with the feed at the reactor temperature the reaction
    heat per kmol acrylonitrile is the figure D-004 and README.md compare with SRC-2."""
    t_in, t_bed = streams["S5"]["temperature"]["value"], streams["S6"]["temperature"]["value"]
    feed_heat = _sensible(streams, mw, comps, "S5", t_in, t_bed)
    _stated(feed_heat / 1e3, "DESIGN.md", r"in the bed from 373 to 713 K \(([0-9.]+) MW")
    acn = kmol(streams, mw, "S6")["ACN"]
    per_kmol = (duty["Q4"] + feed_heat) * 3.6 / acn
    _stated((duty["Q4"] + feed_heat) / 1e3, "DESIGN.md", r"the reaction heat is ([0-9.]+) MW, [0-9]+ MJ per kmol")
    _stated(per_kmol, "DESIGN.md", r"the reaction heat is [0-9.]+ MW, ([0-9]+) MJ per kmol acrylonitrile")
    _stated(per_kmol, "README.md", r"reaction heat is ([0-9]+) MJ per kmol")
    # SRC-2: 59.74 MW at 272.34 kmol/h, and with the 1.40 MW its reaction heat gives the feed
    low, high = (float(x) for x in re.search(r"([0-9]+) to ([0-9]+) % higher per kmol", _text("DESIGN.md")).groups())
    assert round((per_kmol / ((59.74 + 1.40) * 1e3 * 3.6 / 272.34) - 1) * 100) == low
    assert round((per_kmol / (59.74e3 * 3.6 / 272.34) - 1) * 100) == high


def test_lca_links_and_allocation(streams, mw):
    lca = _load("lca/lca.yaml")
    assert lca["functional_unit"]["product"] == "ACNP"
    assert lca["allocation"]["method"] == "mass"
    assert set(lca["allocation"]["coproducts"]) == {"ACNP", "HCNP", "MECNP"}
    masses = {"acrylonitrile": "S27", "HCN": "S25", "acetonitrile": "S22"}
    total = sum(sum(kg(streams, mw, s).values()) for s in masses.values())
    for name, sid in masses.items():  # the shares D-011 states
        share = sum(kg(streams, mw, sid).values()) / total * 100
        _stated(share, "DESIGN.md", rf"Allocation by mass between .*?{name} \(([0-9.]+) %\)", name)
    acn_share = sum(kg(streams, mw, "S27").values()) / total * 100
    _stated(acn_share, "README.md", r"by mass \(([0-9.]+) % to acrylonitrile")
    _stated(100 - acn_share, "lca/lca.yaml", r"together are ([0-9.]+) % of the nitrile mass")
    mappings = _load("lca/mappings.yaml")["exchanges"]
    assert mappings["feed:C3"]["dataset"]["path"].startswith("processes/propylene-pdh-1/")
    assert mappings["feed:AMM"]["dataset"]["path"] == "processes/ammonia-1/lca/dataset.yaml"
    assert mappings["feed:ACID"]["dataset"]["path"] == "processes/sulfuric-acid-1/lca/dataset.yaml"
    for rel in [m["dataset"]["path"] for m in mappings.values() if "dataset" in m]:
        assert (KIT / rel).is_file()
    # the exported steam is never linked (a linked output is booked as consumption, D-011), and no
    # chemistry slug maps it either
    assert "product:HPS" not in mappings
    assert all(f.get("inventory_key") != "product:HPS" for f in _load("process.yaml")["chemistry"]["utilities"])
    # each exclusion's method covers its source kind (core's emission coverage)
    methods = {e["id"]: e["method"] for e in lca["emission_exclusions"]}
    assert methods == {"startup-vent": "non-routine", "column-vents": "flare", "oxidiser-nox": "combustion", "storage-breathing": "storage-tank"}
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
