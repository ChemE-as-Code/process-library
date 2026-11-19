"""mtbe-1 (#509): the folder's stated numbers against its own flowsheet.

Fast and without core: the flowsheet's streams (propagated by core, the duties given by the
source or by scripts/balance.py) are read as YAML, and the statements the folder makes in
DESIGN.md, README.md, process.yaml and lca/ are checked against them:

- the column's feeds, conversion, distillate and bottoms are the ones of Murat et al. (2003,
  Tables 1 and 2), and its duties are that table's;
- the design specifications hold (206 mol/s of methanol to the column, 0.15 kg of wash water per
  kg of distillate), the separators close per component;
- the specific consumptions, the product purity and the washed raffinate stated in process.yaml
  and README.md follow from the streams; DESIGN.md's duty table matches every energy stream;
- the LCI subdivides the raffinate: the isobutene linked to butadiene-1's raffinate-1, the inert
  C4 and the raffinate-2 free; every heat stream reaches the LCI;
- the process is public with CC-BY-4.0 and requires cheme-as-code 1.13.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

KIT = Path(__file__).resolve().parents[1]
PROCESS = KIT / "processes" / "mtbe-1"


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
    return {s["id"]: s["state"]["design"] for s in sheet["streams"] if "state" in s}


def _kmol(state: dict, comps) -> dict[str, float]:
    comp = state["composition"]
    x = {c: v for c, v in comp["values"].items() if v > 0}
    flow = state["flow"]["value"]
    if comp["basis"] == "mole_fraction":
        total = flow / sum(x[c] * comps[c]["molar_mass"] for c in x)
        return {c: total * v for c, v in x.items()}
    return {c: flow * v / comps[c]["molar_mass"] for c, v in x.items()}


def _kg(state: dict, comps) -> dict[str, float]:
    return {c: n * comps[c]["molar_mass"] for c, n in _kmol(state, comps).items()}


def _duty(streams, sid: str) -> float:
    return streams[sid]["duty"]["value"]


def test_the_column_feeds_are_the_sources(streams, comps):
    """Murat et al. (2003) Table 1: 549 mol/s of butenes at 0.356 isobutene, 206 mol/s methanol."""
    ib = _kmol(streams["S1"], comps)["IB"]
    b1 = _kmol(streams["S2"], comps)["B1"]
    assert (ib + b1) / 3.6 == pytest.approx(549, rel=1e-6)
    assert ib / (ib + b1) == pytest.approx(0.356, rel=1e-6)
    assert _kmol(streams["S7"], comps)["MEOH"] / 3.6 == pytest.approx(206, rel=1e-5)
    assert streams["S4"]["temperature"]["value"] == 350.0
    assert streams["S7"]["temperature"]["value"] == 320.0


def test_conversion_and_products_follow_the_source(streams, comps):
    """Murat et al. (2003) Table 2: 99.5 % conversion, bottoms 0.986 MTBE and 0.014 C4 at about
    197 mol/s, distillate about 363.7 mol/s with 0.032 methanol and 0.003 isobutene."""
    ib_in = _kmol(streams["S4"], comps)["IB"] + _kmol(streams["S7"], comps).get("IB", 0.0)
    bot = _kmol(streams["S10"], comps)
    top = _kmol(streams["S9"], comps)
    assert bot["MTBE"] / ib_in == pytest.approx(0.995, rel=1e-6)
    total_bot = sum(bot.values())
    assert total_bot / 3.6 == pytest.approx(197, rel=2e-3)
    assert bot["MTBE"] / total_bot == pytest.approx(0.986, abs=2e-4)
    total_top = sum(top.values())
    assert total_top / 3.6 == pytest.approx(363.7, rel=2e-3)
    assert top["MEOH"] / total_top == pytest.approx(0.032, abs=5e-4)
    assert top["IB"] / total_top == pytest.approx(0.003, abs=5e-4)


def test_the_column_duties_are_the_sources(streams):
    assert _duty(streams, "Q3") == 39300.0
    assert _duty(streams, "Q4") == 49700.0


@pytest.mark.parametrize("node", ["C101", "C201", "C202"])
def test_separators_close_per_component(sheet, streams, comps, node):
    ins = [s["id"] for s in sheet["streams"] if s.get("to", "").startswith(node + ".") and s.get("kind") != "energy"]
    outs = [s["id"] for s in sheet["streams"] if s.get("from", "").startswith(node + ".") and s.get("kind") != "energy"]
    total_in: dict[str, float] = {}
    total_out: dict[str, float] = {}
    for sid in ins:
        for c, v in _kg(streams[sid], comps).items():
            total_in[c] = total_in.get(c, 0.0) + v
    for sid in outs:
        for c, v in _kg(streams[sid], comps).items():
            total_out[c] = total_out.get(c, 0.0) + v
    for c, v in total_in.items():
        assert total_out.get(c, 0.0) == pytest.approx(v, rel=1e-4, abs=0.05), (node, c)


def test_the_wash_and_the_raffinate_2(streams, comps):
    assert streams["S13"]["flow"]["value"] / streams["S12"]["flow"]["value"] == pytest.approx(0.15, rel=1e-5)
    raf = _kg(streams["S14"], comps)
    total = sum(raf.values())
    assert raf["MEOH"] / total * 1e6 == pytest.approx(9.4, abs=0.5)  # US 5 336 841 A: about 10 wppm
    assert raf["H2O"] / total * 1e6 == pytest.approx(400, abs=5)
    ext = _kg(streams["S15"], comps)
    assert ext["MEOH"] / sum(ext.values()) == pytest.approx(0.109, abs=5e-4)


def test_the_stated_consumptions_and_the_product(streams, comps):
    product = streams["S11"]["flow"]["value"]
    assert product * 8000 / 1e6 == pytest.approx(498.2, abs=0.1)
    kg = _kg(streams["S11"], comps)
    assert kg["MTBE"] / sum(kg.values()) == pytest.approx(0.9910, abs=5e-5)
    per = {s: streams[s]["flow"]["value"] / product for s in ("S1", "S2", "S5", "S21")}
    assert per["S1"] == pytest.approx(0.634, abs=5e-4)
    assert per["S2"] == pytest.approx(1.147, abs=5e-4)
    assert per["S5"] == pytest.approx(0.360, abs=5e-4)
    mps = _duty(streams, "Q3") / product
    lps = sum(_duty(streams, q) for q in ("Q1", "Q2", "Q7")) / product
    cw = sum(_duty(streams, q) for q in ("Q4", "Q5", "Q6", "Q8", "Q9")) / product
    power = (_duty(streams, "P1") + _duty(streams, "P2")) / product
    assert (round(mps, 3), round(lps, 3), round(cw, 3), round(power, 4)) == (0.631, 0.245, 0.934, 0.0038)
    # the inert C4: most returns in the raffinate-2, 0.009 kg/kg leaves in the product (D-010)
    c4_product = kg["B1"] / product
    c4_returned = _kg(streams["S14"], comps)["B1"] / product
    assert c4_product == pytest.approx(0.0090, abs=5e-5)
    assert c4_returned == pytest.approx(1.138, abs=5e-4)
    assert c4_product + c4_returned == pytest.approx(per["S2"], rel=1e-4)
    text = _text("process.yaml") + _text("README.md")
    for stated in ("0.634 kg", "1.147 kg", "0.009 kg", "0.360 kg", "0.631 kWh", "0.245 kWh", "0.934 kWh", "0.0038 kWh", "99.10 wt%", "99.5 %"):
        assert stated in text, stated


def test_design_md_duty_table_matches(streams):
    design = _text("DESIGN.md")
    for sid in [f"Q{i}" for i in range(1, 10)] + ["P1", "P2"]:
        assert f"| {sid} | {_duty(streams, sid):.1f} |" in design, sid


def test_every_heat_stream_reaches_the_lci(sheet):
    lca = _load("lca/lca.yaml")
    keys = {f["key"] for f in lca["flows"]}
    for terminal in ("feed:LPS", "feed:MPS", "feed:POWER", "product:CW"):
        assert terminal in keys
    for s in sheet["streams"]:
        if s.get("kind") == "energy":
            ends = {s["from"].split(".")[0], s["to"].split(".")[0]}
            assert ends & {"LPS", "MPS", "POWER", "CW"}, s["id"]


def test_the_raffinate_is_subdivided():
    flows = {f["key"]: f for f in _load("lca/lca.yaml")["flows"]}
    assert flows["feed:C4I"].get("free") is True
    assert flows["product:RAF2"].get("free") is True
    assert "allocation" not in _load("lca/lca.yaml")
    mappings = _load("lca/mappings.yaml")["exchanges"]
    assert mappings["feed:IBC"]["dataset"]["product"] == "product:c4-raffinate"
    assert (KIT / mappings["feed:IBC"]["dataset"]["path"]).is_file()
    assert mappings["feed:MEOH"]["dataset"]["path"] == "processes/methanol-1/lca/dataset.yaml"
    dataset = _load("lca/dataset.yaml")
    products = [e["key"] for e in dataset["exchanges"] if e["type"] == "product"]
    assert products == ["product:MTBEP"]


def test_public_and_core_version():
    manifest = _load("process.yaml")
    assert manifest["publication"] == {"status": "public", "license": "CC-BY-4.0"}
    assert _load("plant.yaml")["requires"] == "cheme-as-code>=1.13"
