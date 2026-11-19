"""vinyl-acetate-1 (#479): the folder's stated numbers against its own flowsheet.

Fast and without core: the flowsheet's streams (propagated by core, the duties given by
scripts/balance.py) are read as YAML, and the statements the folder makes in DESIGN.md,
README.md, process.yaml, lca/ and the benchmarks are checked against them:

- the reactor feed meets the source's Table 2 composition (US 8 765 995 B2), the conversions
  follow from its space-time yield, GHSV and selectivity, and the heats of reaction from the
  ideal-gas data agree with the patent's -176 and -1324 kJ/mol;
- the specific consumptions, the product purity, the vented CO2 and the ethylene yield stated
  in process.yaml and README.md follow from the streams;
- the separators' outlets close on their inlets per component, and C-101's organic phase lies
  inside US 8 410 307 B2's composition;
- R-101's heat covers the steam users but Q9, and Q1 is what is left after Q2, Q7 and Q11;
  DESIGN.md's duty table matches every energy stream;
- the script's vapour is the ideal-gas monomer of the formation enthalpies, every adiabatic
  mixer closes its energy balance, the scrubbed gas holds the acid of the lean scrub acid,
  C-101 takes off its aqueous phase and C-202's bottoms are drier than its side draw;
- every heat stream reaches the LCI, the feeds are linked to their library producers, and the
  benchmark range follows from the patent's selectivities;
- the process is public with CC-BY-4.0 and requires cheme-as-code 1.12.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest
import yaml

KIT = Path(__file__).resolve().parents[1]
PROCESS = KIT / "processes" / "vinyl-acetate-1"


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
    x = comp["values"]
    flow = state["flow"]["value"]
    if comp["basis"] == "mole_fraction":
        total = flow / sum(x[c] * comps[c]["molar_mass"] for c in x)
        return {c: total * v for c, v in x.items()}
    return {c: flow * v / comps[c]["molar_mass"] for c, v in x.items()}


def _kg(state: dict, comps) -> dict[str, float]:
    return {c: n * comps[c]["molar_mass"] for c, n in _kmol(state, comps).items()}


def _duty(streams, sid: str) -> float:
    return streams[sid]["duty"]["value"]


def test_the_reactor_feed_is_the_sources_table_2(streams, comps):
    x = _kmol(streams["S9"], comps)
    total = sum(x.values())
    assert x["C2H4"] / total == pytest.approx(0.65, abs=2e-4)
    assert x["ACOH"] / total == pytest.approx(0.123, abs=2e-4)
    assert x["O2"] / total == pytest.approx(0.086, abs=2e-4)


def test_the_conversions_follow_from_sty_ghsv_and_selectivity():
    reactions = {r["id"]: r for r in _load("process/reactions.yaml")["reactions"]}
    vam_per_feed = (900 / 86.09) / (3750 / 22.414)
    burnt = vam_per_feed / 0.910 - vam_per_feed
    assert reactions["ACX"]["conversion"]["value"] == pytest.approx(vam_per_feed / 0.65, abs=1e-4)
    assert reactions["COMB"]["conversion"]["value"] == pytest.approx(burnt / 0.65, abs=1e-4)


def test_the_reactor_makes_what_the_conversions_say(streams, comps):
    i, o = _kmol(streams["S9"], comps), _kmol(streams["S10"], comps)
    assert (o["VAM"] - i["VAM"]) / i["C2H4"] == pytest.approx(0.0961, rel=1e-3)
    assert (o["CO2"] - i["CO2"]) / 2 / i["C2H4"] == pytest.approx(0.0095, rel=1e-3)
    # DESIGN.md D-004: oxygen conversion 58 %, oxygen selectivity 63 %
    assert 1 - o["O2"] / i["O2"] == pytest.approx(0.58, abs=0.005)
    assert 0.5 * (o["VAM"] - i["VAM"]) / (i["O2"] - o["O2"]) == pytest.approx(0.63, abs=0.005)


def test_the_ideal_gas_data_give_the_patents_heats_of_reaction(comps):
    hf = {c: comps[c]["ideal_gas"]["dHf_298"] / 1000 for c in comps}
    acx = hf["VAM"] + hf["H2O"] - hf["C2H4"] - hf["ACOH"]
    comb = 2 * hf["CO2"] + 2 * hf["H2O"] - hf["C2H4"]
    assert acx == pytest.approx(-176, abs=1.0)
    assert comb == pytest.approx(-1324, abs=1.5)


def test_the_stated_consumptions_and_the_product(streams, comps):
    product = streams["S33"]["flow"]["value"]
    vam_kg = _kg(streams["S33"], comps)["VAM"]
    assert vam_kg * 8000 / 1000 == pytest.approx(200_000, rel=1e-4)
    per = {s: streams[s]["flow"]["value"] / product for s in ("S1", "S4", "S7")}
    assert per["S1"] == pytest.approx(0.370, abs=5e-4)
    assert per["S4"] == pytest.approx(0.703, abs=5e-4)
    assert per["S7"] == pytest.approx(0.299, abs=5e-4)
    kg = _kg(streams["S33"], comps)
    assert kg["VAM"] / sum(kg.values()) == pytest.approx(0.9999, abs=5e-5)
    assert kg["H2O"] / sum(kg.values()) * 1e6 == pytest.approx(90, abs=1)
    assert kg["H2O"] / sum(kg.values()) * 1e6 <= 100  # US 8 410 307 B2: <= 100 ppm water
    co2 = _kg(streams["S21"], comps)["CO2"] / product
    assert co2 == pytest.approx(0.0995, abs=5e-5)
    eth_in = _kmol(streams["S1"], comps)["C2H4"]
    vam_out = _kmol(streams["S33"], comps)["VAM"]
    assert vam_out / eth_in == pytest.approx(0.881, abs=5e-4)
    text = _text("process.yaml") + _text("README.md")
    for stated in ("0.370 kg", "0.703 kg", "0.299 kg", "0.0995 kg", "88.1 %", "99.99 wt%"):
        assert stated in text


@pytest.mark.parametrize("node", ["C101", "C102", "C104", "A101", "C201", "C202"])
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


def test_c101s_organic_phase_inside_the_sources_composition(streams, comps):
    kg = _kg(streams["S13"], comps)
    vam = kg["VAM"] / sum(kg.values())
    water = kg["H2O"] / sum(kg.values())
    assert 0.90 <= vam <= 0.99  # US 8 410 307 B2: 90-99 wt% VAM, 0.5-8 wt% water
    assert 0.005 <= water <= 0.08
    assert vam == pytest.approx(0.989, abs=5e-4)  # DESIGN.md D-005 states 98.9 wt%


def test_reactor_steam_and_the_import(streams):
    q1, q2, q7, q11, q9 = (_duty(streams, q) for q in ("Q1", "Q2", "Q7", "Q11", "Q9"))
    r101 = q1 + q2 + q7 + q11
    assert r101 == pytest.approx(23697, rel=2e-3)
    assert q9 > 0
    assert q9 == pytest.approx(6182.2, abs=1)
    assert "23.7 MW" in _text("README.md") and "6.18 MW" in _text("README.md")
    design = _text("DESIGN.md")
    for sid in [f"Q{i}" for i in range(1, 14)] + ["P1"]:
        assert f"| {sid} | {_duty(streams, sid):.1f} |" in design, sid


def _balance_module():
    spec = importlib.util.spec_from_file_location("va1_balance", PROCESS / "scripts" / "balance.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_the_vapour_is_the_ideal_gas_monomer_of_the_formation_enthalpies(comps):
    """The script's heats of vaporization are Hf(gas) - Hf(liquid) of chemicals 1.5.2 (CRC for
    acetic acid and vinyl acetate, ATcT for water), on the gas values of materials.yaml: not the
    heat of vaporization to acetic acid's associated vapour (23.4 kJ/mol)."""
    hvap = _balance_module().HVAP_298
    hf_liquid = {"ACOH": -484300.0, "VAM": -349200.0, "H2O": -285825.0}
    for c, hl in hf_liquid.items():
        assert hvap[c] == pytest.approx(comps[c]["ideal_gas"]["dHf_298"] - hl, abs=1.0), c


@pytest.mark.parametrize("out, ins", [
    ("S3", ("S1", "S2")), ("S8", ("S6", "S7")), ("S24", ("S22", "S23")),
    ("S25", ("S14", "S17", "S31", "S37")), ("S29", ("S13", "S26")), ("S34", ("S38", "S27", "S30")),
])
def test_the_mixers_close_their_energy_balance(sheet, out, ins):
    """Every mixer is adiabatic (no energy port): its outlet's temperature in the flowsheet gives
    the inlets' enthalpy on the script's basis, within 5 kW."""
    bal = _balance_module()
    comps = {c["id"]: c for c in _load("process/materials.yaml")["components"]}
    streams = {s["id"]: s for s in sheet["streams"] if s.get("kind") != "energy"}

    def h(sid):
        st = streams[sid]["state"]["design"]
        phase = st.get("phase", {}).get("value", "vapor")
        return bal.enthalpy(bal.kmol(streams[sid], comps), st["temperature"]["value"], phase, comps)

    assert h(out) == pytest.approx(sum(h(s) for s in ins), abs=5.0)


def test_the_scrubbed_gas_holds_the_acid_of_the_lean_scrub_acid(streams, comps):
    """C-102's gas leaves near equilibrium with the lean acid S15 (0.43 mol% at 313 K by Dortmund
    UNIFAC, DESIGN.md D-005), not below it; C-104 then washes 99 % of the slip's acid to C-201."""
    gas = _kmol(streams["S16"], comps)
    assert gas["ACOH"] / sum(gas.values()) == pytest.approx(0.0041, abs=1e-4)
    slip, washed = _kmol(streams["S20"], comps), _kmol(streams["S36"], comps)
    assert washed["ACOH"] / slip["ACOH"] == pytest.approx(0.01, rel=1e-3)


def test_c101_takes_off_its_aqueous_phase_and_c202_is_driest_at_the_bottom(sheet, streams, comps):
    """SRC-2's claim 1 step c: C-101's decanter's aqueous phase S38 is taken off (to the effluent);
    C-202's bottoms S31 lie below the side draw S32 and are drier than it (D-005, D-007)."""
    s38 = next(s for s in sheet["streams"] if s["id"] == "S38")
    assert s38["from"] == "C101.aq" and s38["to"].startswith("M203.")
    aq = _kmol(streams["S38"], comps)
    assert aq["H2O"] / sum(aq.values()) > 0.98
    x31, x32 = _kmol(streams["S31"], comps), _kmol(streams["S32"], comps)
    assert x31["H2O"] / sum(x31.values()) < x32["H2O"] / sum(x32.values())
    assert streams["S32"]["temperature"]["value"] == pytest.approx(361.3, abs=0.1)


def test_every_heat_stream_reaches_the_lci(sheet):
    lca = _load("lca/lca.yaml")
    keys = {f["key"] for f in lca["flows"]}
    for s in sheet["streams"]:
        if s.get("kind") != "energy":
            continue
        a, b = s["from"].split(".")[0], s["to"].split(".")[0]
        if "LPS" in (a, b):
            assert "feed:LPS" in keys
        if "POWER" in (a, b):
            assert "feed:POWER" in keys
        if "CW" in (a, b):
            assert "product:CW" in keys


def test_the_feeds_are_linked_to_their_library_producers():
    maps = _load("lca/mappings.yaml")["exchanges"]
    assert maps["feed:ETH"]["dataset"]["path"] == "processes/ethylene-1/lca/dataset.yaml"
    assert maps["feed:ACF"]["dataset"]["path"] == "processes/acetic-acid-1/lca/dataset.yaml"
    assert maps["feed:OXY"]["dataset"]["path"] == "processes/asu-1/lca/dataset.yaml"
    for rel in ("ethylene-1", "acetic-acid-1", "asu-1"):
        assert (KIT / "processes" / rel / "lca" / "dataset.yaml").exists()


def test_the_benchmark_range_follows_from_the_selectivities():
    bench = yaml.safe_load((KIT / "benchmarks" / "oxygenates.yaml").read_text(encoding="utf-8"))
    ref = bench["kpis"]["vam-specific-ethylene"]["references"][0]
    floor = 28.054 / 86.090
    assert ref["range"][0] == pytest.approx(floor / 0.934, abs=1e-4)
    assert ref["range"][1] == pytest.approx(floor / 0.909, abs=1e-4)


def test_the_balance_script_cites_every_value_it_gives(sheet):
    cited = [s["id"] for s in sheet["streams"] if "scripts/balance.py" in str(s.get("state", ""))]
    assert {"Q2", "Q3", "Q9", "Q13", "P1", "S2", "S3", "S8", "S24", "S25", "S29", "S34", "S37"} <= set(cited)
    q1 = next(s for s in sheet["streams"] if s["id"] == "Q1")
    assert q1["state"]["design"]["duty"]["provenance"] == "calculated"


def test_published_public_with_cc_by():
    manifest = _load("process.yaml")
    assert manifest["publication"] == {"status": "public", "license": "CC-BY-4.0"}


def test_requires_core_1_12():
    assert _load("plant.yaml")["requires"] == "cheme-as-code>=1.12"


def test_recycle_acid_inside_the_sources_range(streams, comps):
    kg = _kg(streams["S28"], comps)
    acid = kg["ACOH"] / sum(kg.values())
    assert 0.70 <= acid <= 0.95  # US 6 420 595 B1: 70-95 % acetic acid in water
    assert acid == pytest.approx(0.933, abs=5e-4)
