"""sodium-chlorate-1 (#512): the folder's stated numbers against its own files.

Fast, without core where it can be: the flowsheet's streams (propagated by core) are read as
YAML, and the statements the folder makes in DESIGN.md, README.md, process.yaml and lca/lca.yaml
are checked against them:

- the salt, water and electricity per kg of product and their BREF ranges;
- the cell's Faraday extents (process/cells.yaml) equal the flowsheet's chlorate and oxygen
  extents, and the cell gas holds the stated oxygen;
- the cell feed's chlorate and chloride content and the circulation against US 5 419 818 A;
- the reaction-tank volume of D-007 from the open rate constant;
- the energy streams' arithmetic (rectifiers, heat recovery, the returned liquor's reheat,
  condenser) and the hypochlorite at the crystallizer against the BREF's H2O2;
- the hydrogen per t and the vent against the BREF;
- the allocation shares are the contained products' masses, the consumables' per-year amounts
  their per-t rates;
- with core: cheme process cell gives the DC power and heat the flowsheet carries;
- the process is public with CC-BY-4.0 and requires cheme-as-code 1.12.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

KIT = Path(__file__).resolve().parents[1]
PROCESS = KIT / "processes" / "sodium-chlorate-1"
F = 96485.33212  # C/mol, CODATA 2018
RHO = 1.40  # kg/L, the liquor density ASSUMED in D-005


def _load(rel: str) -> dict:
    return yaml.safe_load((PROCESS / rel).read_text(encoding="utf-8"))


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


def _flow(streams, sid: str) -> float:
    s = streams[sid]
    return s["flow"]["value"] if "flow" in s else s["duty"]["value"]


def _kg(streams, mw, sid: str) -> dict[str, float]:
    """kg/h by component of a material stream."""
    s = streams[sid]
    total = s["flow"]["value"]
    comp = s["composition"]
    if comp["basis"] == "mass_fraction":
        return {n: total * x for n, x in comp["values"].items()}
    mass = {n: x * mw[n] for n, x in comp["values"].items()}
    m = sum(mass.values())
    return {n: total * v / m for n, v in mass.items()}


def _kmol(streams, mw, sid: str) -> dict[str, float]:
    return {n: v / mw[n] for n, v in _kg(streams, mw, sid).items()}


def test_specific_consumptions_and_their_bref_ranges(streams):
    product = _flow(streams, "S20")
    salt = _flow(streams, "S1") / product
    water = _flow(streams, "S2") / product
    power = (_flow(streams, "P1") + _flow(streams, "P3")) / product
    assert salt == pytest.approx(0.550, abs=5e-4)
    assert water == pytest.approx(0.545, abs=5e-4) and 0.4 <= water <= 2.7
    assert power == pytest.approx(5.196, abs=5e-4) and 5.0 <= power <= 6.0
    manifest = _text("process.yaml")
    assert "0.550 kg/kg" in manifest and "0.545 kg/kg" in manifest and "5.196 kWh/kg" in manifest


def test_the_cells_extents_equal_the_flowsheets(streams, mw):
    cell = _load("process/cells.yaml")["cells"][0]
    current = cell["current"]["value"] * 1000 * cell["cells"]  # A
    fe = cell["faradaic_efficiency"]["value"]
    f_o2 = cell["side_reactions"][0]["current_fraction"]["value"]
    chlorate = fe * current / (6 * F) * 3.6  # kmol/h
    oxygen = f_o2 * current / (4 * F) * 3.6
    made = _kmol(streams, mw, "S9")["NaClO3"] - _kmol(streams, mw, "S8")["NaClO3"]
    assert made == pytest.approx(chlorate, rel=1e-4)
    assert _kmol(streams, mw, "S10")["O2"] == pytest.approx(oxygen, rel=1e-3)
    # L-7: the cells' HYPO (one H2 per extent) is 3 CHLORATE + 2 WATER_SPLIT of the cell model
    hypo = _kmol(streams, mw, "S8")["H2"] - _kmol(streams, mw, "S7")["H2"]
    assert hypo == pytest.approx(3 * chlorate + 2 * oxygen, rel=1e-4)
    gas = _kmol(streams, mw, "S10")
    y_o2 = gas["O2"] / (gas["O2"] + gas["H2"])
    assert y_o2 == pytest.approx(0.0221, abs=1e-4) and 0.02 <= y_o2 <= 0.025
    # 2.5 kA/m2 inside the BREF's 1.0-3.0 kA/m2
    density = cell["current"]["value"] * 1000 / cell["active_area"]["value"]
    assert density == pytest.approx(2500, abs=1)


def test_the_cell_feed_and_the_circulation(streams, mw):
    feed = _kg(streams, mw, "S6")
    total = _flow(streams, "S6")
    assert feed["NaClO3"] / total == pytest.approx(0.40357, abs=1e-5)
    nacl_g_l = feed["NaCl"] / total * RHO * 1000
    assert 110 <= nacl_g_l <= 125 and nacl_g_l == pytest.approx(121, abs=0.5)
    m3_per_t = total / RHO / 1000 / (_kg(streams, mw, "S20")["NaClO3_s"] / 1000)
    assert 75 <= m3_per_t <= 200 and m3_per_t == pytest.approx(98, abs=0.5)


def test_the_reaction_tank_volume_from_the_rate_constant(streams, mw):
    k1, k3, ph = 7.19, 2e-7, 6.4  # mol-2 dm6 s-1 and mol/L at 70 C (Spasojevic et al. 2018)
    h = 10 ** -ph
    x = h / (h + k3)
    total = _flow(streams, "S9")
    c = _kg(streams, mw, "S9")["NaOCl"] / mw["NaOCl"] * 1000 / (total / RHO)  # mol/h over L/h
    rate = k1 * x**2 * (1 - x) * c**3  # mol/(L s)
    made = _kmol(streams, mw, "S9")["NaClO3"] - _kmol(streams, mw, "S8")["NaClO3"]
    volume = 3 * made / 3.6 / rate / 1000  # m3
    assert volume == pytest.approx(648, abs=1)
    assert volume / (total / RHO / 1000) == pytest.approx(1.06, abs=0.01)
    assert "648 m3" in _text("DESIGN.md") and "1.06 h" in _text("DESIGN.md")


def test_the_energy_streams(streams, mw):
    p1, p2, q1 = _flow(streams, "P1"), _flow(streams, "P2"), _flow(streams, "Q1")
    assert p1 == pytest.approx(p2 / 0.97, abs=0.01) and q1 == pytest.approx(p1 - p2, abs=0.01)
    q2, q3, q4, q7 = (_flow(streams, q) for q in ("Q2", "Q3", "Q4", "Q7"))
    # the crystallizer's duty nets the side stream's cooling from 343.15 to 323.15 K
    assert q3 == pytest.approx(_flow(streams, "S17") * 2382 / 3600 - _flow(streams, "S13") * 2.9 * 20 / 3600, abs=0.5)
    # Q7: the returned liquor and the make-up brought back to the loop's 343.15 K (D-009)
    t = {s: streams[s]["temperature"]["value"] for s in ("S1", "S2", "S3", "S4", "S5", "S6")}
    cp = {"S1": 0.872, "S2": 4.18, "S3": 2.9, "S4": 4.18}
    reheat = sum(_flow(streams, s) * cp[s] * (t["S6"] - t[s]) for s in cp)  # kJ/h
    assert q7 == pytest.approx(reheat / 3600, abs=0.01)
    assert t["S5"] == pytest.approx(t["S6"] - reheat / (_flow(streams, "S5") * 2.9), abs=0.01)
    assert q4 == pytest.approx(q2 - q3 - q7, abs=0.01)
    assert _flow(streams, "Q5") == pytest.approx(_flow(streams, "S17") * 2382 / 3600, abs=0.01)
    assert q2 / p2 == pytest.approx(0.484, abs=0.001)  # the BREF: about 50 % of the energy
    formed = (_kmol(streams, mw, "S9")["NaClO3"] - _kmol(streams, mw, "S8")["NaClO3"]) * mw["NaClO3"]
    assert p1 / formed * 1000 == pytest.approx(4919, abs=1) and 4700 <= p1 / formed * 1000 <= 5200
    cw = (q1 + q4 + _flow(streams, "Q5")) / _flow(streams, "S20")
    assert cw == pytest.approx(2.42, abs=0.005) and "2.42 kWh/kg" in _text("process.yaml")


def test_the_hypochlorite_at_the_crystallizer(streams, mw):
    # D-007: reducing the side stream's 3 g/L takes 16 kg H2O2 per t, against the BREF's 2 kg/t
    product_t = _flow(streams, "S20") / 1000
    naocl = _kmol(streams, mw, "S13")["NaOCl"]
    assert naocl == pytest.approx(3.01, abs=0.005)
    h2o2 = naocl * 34.0147  # kg/h, one H2O2 per NaOCl
    assert h2o2 == pytest.approx(102.3, abs=0.05) and h2o2 / product_t == pytest.approx(16.1, abs=0.05)
    bref = 2.0 * product_t / 34.0147 * mw["NaOCl"] / _flow(streams, "S13") * RHO * 1000  # g/L
    assert bref == pytest.approx(0.38, abs=0.005)
    assert "16.1 kg per t" in _text("DESIGN.md") and "about 0.38 g/L" in _text("DESIGN.md")


def test_hydrogen_per_t_and_the_vent(streams, mw):
    product = _flow(streams, "S20")
    h2 = _kg(streams, mw, "S10")["H2"]
    assert h2 / (product / 1000) == pytest.approx(59.3, abs=0.1)
    vent = _kg(streams, mw, "S22")["H2"] / product * 1000  # g/kg
    assert vent == pytest.approx(18.4, abs=0.05) and 9 <= vent <= 28


def test_the_allocation_shares_are_the_contained_masses(streams, mw):
    lca = _load("lca/lca.yaml")
    product = _flow(streams, "S20")
    h2 = _kg(streams, mw, "S21")["H2"]
    shares = lca["allocation"]["shares"]
    assert shares["NACLO3P"] == pytest.approx(product / (product + h2), abs=1e-4)
    assert shares["H2P"] == pytest.approx(h2 / (product + h2), abs=1e-4)


def test_the_consumables_are_their_per_t_rates(streams):
    tonnes = round(_flow(streams, "S20") * 8000 / 1000)  # 50 806 t/a, as lca.yaml states
    assert tonnes == 50806
    per_t = {"sodium-hydroxide": 45.0, "hydrochloric-acid": 22.5 / 0.33, "sodium-carbonate": 1.02,
             "sodium-dichromate": 0.08, "hydrogen-peroxide": 4.0, "nitrogen": 3.2}
    consumables = {c["id"]: c["per_year"] for c in _load("lca/lca.yaml")["consumables"]}
    assert set(consumables) == set(per_t)
    for cid, rate in per_t.items():
        assert consumables[cid] == pytest.approx(rate * tonnes, abs=1.0), cid


def test_the_benchmarks_bind_the_dataset():
    bench = yaml.safe_load((KIT / "benchmarks" / "inorganic-chemicals.yaml").read_text(encoding="utf-8"))
    entry = next(d for d in bench["datasets"] if d["process"] == "sodium-chlorate-1")
    dataset = _load("lca/dataset.yaml")
    ids = [d.get("id") for d in (dataset if isinstance(dataset, list) else dataset.get("datasets", [dataset]))]
    assert entry["dataset"] in ids
    assert set(entry["kpis"]) == {"naclo3-specific-salt", "naclo3-specific-electricity", "naclo3-specific-water"}


def test_published_public_with_cc_by():
    assert _load("process.yaml")["publication"] == {"status": "public", "license": "CC-BY-4.0"}


def test_requires_core_1_12():
    assert _load("plant.yaml")["requires"] == "cheme-as-code>=1.12"
    assert "Needs cheme-as-code 1.12.0" in _text("README.md") and "Needs cheme-as-code 1.12.0" in _text("process.yaml")


# ---- with core ----------------------------------------------------------------------------


def test_core_cell_gives_the_flowsheets_power_and_heat(streams, mw):
    pytest.importorskip("chemeascode")
    import json

    from chemeascode.domains.process.electrochemical_cell import cell_report

    report = json.loads(cell_report(PROCESS).to_json())
    cell = report["cells"][0]
    assert cell["power_kw"] == pytest.approx(_flow(streams, "P2"), abs=0.05)
    assert cell["heat_duty_kw"] == pytest.approx(_flow(streams, "Q2"), abs=0.05)
    made = _kmol(streams, mw, "S9")["NaClO3"] - _kmol(streams, mw, "S8")["NaClO3"]
    assert cell["extents"]["CHLORATE"] == pytest.approx(made, rel=1e-4)
