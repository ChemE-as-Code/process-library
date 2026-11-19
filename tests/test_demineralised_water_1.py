"""demineralised-water-1 (#470): the folder's stated numbers against its own flowsheet.

Fast and without core: the flowsheet's streams (propagated by core, given by scripts/balance.py)
are read as YAML, and the statements the folder makes in DESIGN.md, README.md, process.yaml,
the equipment list and the LCI are checked against them:

- the product rate, the raw water, the wastewater and the specific consumptions per m3 follow
  from S1, S11, S13, S14, S16 and S18 and the energy streams;
- the splits written in the flowsheet are the script's (backwash share, RO salt passage) and the
  regeneration water is the script's dilution and rinse water;
- the RO's water recovery and the product's residual salt are the stated ones;
- the trim acid brings the acid equivalents to 1.001 times the caustic's, and the neutralised
  effluent carries no caustic;
- the mixed bed's salt load of a run stays within half of the resins' low-end operating
  capacity (DESIGN.md D-005, in kmol);
- the pump powers are V dP / eta at the stated pressures;
- the LCI's inventory is the flowsheet's per kg of product, the raw water is a water resource,
  the acid and the caustic link library producers whose datasets exist, and the wastewater is a
  discharge (water and salt to fresh surface water), not utility-wwtp's treatment;
- the registry grade and the market of the product exist;
- the process is public with CC-BY-4.0 and requires cheme-as-code 1.12.
"""

from __future__ import annotations

import csv
import importlib.util
from pathlib import Path

import pytest
import yaml

KIT = Path(__file__).resolve().parents[1]
PROCESS = KIT / "processes" / "demineralised-water-1"


def _load(rel: str, root: Path = PROCESS) -> dict:
    return yaml.safe_load((root / rel).read_text(encoding="utf-8"))


def _text(rel: str) -> str:
    return " ".join((PROCESS / rel).read_text(encoding="utf-8").split())


@pytest.fixture(scope="module")
def sheet() -> dict:
    return _load("process/flowsheet.yaml")


@pytest.fixture(scope="module")
def streams(sheet) -> dict[str, dict]:
    return {s["id"]: s["state"]["design"] for s in sheet["streams"] if "state" in s}


@pytest.fixture(scope="module")
def balance():
    spec = importlib.util.spec_from_file_location("demin_balance", PROCESS / "scripts" / "balance.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def design(balance) -> dict:
    return balance.design()


def _step(sheet: dict, sid: str) -> dict:
    return next(s for s in sheet["steps"] if s["id"] == sid)


def _kg(balance, streams, sid: str) -> dict[str, float]:
    """Component flows (kg/h) of a stream from its flow and composition (mass or mole basis)."""
    state = streams[sid]
    flow, comp = state["flow"]["value"], state["composition"]
    values = comp["values"]
    if comp["basis"] == "mass_fraction":
        return {c: flow * x for c, x in values.items()}
    mass = {c: x * balance.M[c] for c, x in values.items()}
    total = sum(mass.values())
    return {c: flow * m / total for c, m in mass.items()}


def test_the_product_rate_and_the_specific_numbers(balance, design, streams):
    product = streams["S11"]["flow"]["value"]
    assert product == pytest.approx(50000.0, rel=1e-5)
    raw = streams["S1"]["flow"]["value"]
    assert raw == pytest.approx(design["raw"], rel=1e-5)
    assert raw / product == pytest.approx(1.405, abs=5e-4)
    ww = streams["S18"]["flow"]["value"]
    assert ww / product == pytest.approx(0.405, abs=5e-4)
    acid = streams["S13"]["flow"]["value"] + streams["S16"]["flow"]["value"]
    assert acid / (product / 1000) == pytest.approx(0.2535, abs=5e-5)
    assert streams["S14"]["flow"]["value"] / (product / 1000) == pytest.approx(0.1833, abs=5e-5)
    power = sum(streams[e]["duty"]["value"] for e in ("E1", "E2", "E3", "E4"))
    assert power == pytest.approx(49.70, abs=0.01)
    assert power / (product / 1000) == pytest.approx(0.99, abs=0.005)
    readme, design_md, manifest = _text("README.md"), _text("DESIGN.md"), _text("process.yaml")
    for text in (readme, manifest):
        assert "0.99 kWh per m3" in text
    assert "1.405 kg of raw water" in design_md and "0.405 kg per kg of product" in design_md
    salt = _kg(balance, streams, "S18")["NaCl"] / product * 1000
    assert salt == pytest.approx(0.84, abs=0.005)  # g per kg of product, DESIGN.md D-006


def test_the_splits_are_the_scripts(balance, design, sheet, streams):
    assert _step(sheet, "F101")["split"]["bw"] == pytest.approx(design["bw_share"], rel=1e-5)
    perm = _step(sheet, "M101")["recovery"]["outlets"]["perm"]
    assert perm["H2O"] == balance.RECOVERY
    assert perm["NaCl"] == pytest.approx(design["passage"], rel=1e-5)
    assert _step(sheet, "X201")["recovery"]["outlets"]["prod"]["NaCl"] == balance.NACL_TO_PRODUCT
    spec = next(s for s in sheet["specs"] if s["id"] == "REGEN_WATER")
    assert spec["target"]["value"] == pytest.approx(design["regen_water"], abs=1e-3)
    assert streams["S9"]["flow"]["value"] == pytest.approx(design["regen_water"], rel=1e-5)
    # the permeate carries about 9 mg/kg of salt and the product 0.02 mg/kg
    s6 = _kg(balance, streams, "S6")
    assert s6["NaCl"] / streams["S6"]["flow"]["value"] * 1e6 == pytest.approx(9.2, abs=0.1)
    s11 = _kg(balance, streams, "S11")
    assert s11["NaCl"] / streams["S11"]["flow"]["value"] * 1e6 == pytest.approx(0.0185, abs=0.002)


def test_the_ro_recovers_75_percent_of_the_water(balance, streams):
    feed, perm = _kg(balance, streams, "S5"), _kg(balance, streams, "S6")
    assert perm["H2O"] / feed["H2O"] == pytest.approx(0.75, rel=1e-4)


def test_the_trim_acid_neutralises_the_caustic(balance, design, streams):
    acid = (streams["S13"]["flow"]["value"] + streams["S16"]["flow"]["value"]) * 0.33 / balance.M["HCl"]
    caustic = streams["S14"]["flow"]["value"] * 0.5 / balance.M["NaOH"]
    assert acid / caustic == pytest.approx(balance.TRIM, abs=2e-4)
    effluent = _kg(balance, streams, "S17")
    assert effluent["NaOH"] == 0.0
    assert effluent["HCl"] < 0.01 * streams["S16"]["flow"]["value"] * 0.33
    # the regenerants' equivalents against the salt the beds take up (DESIGN.md D-005)
    assert design["ratio_hcl"] == pytest.approx(9.6, abs=0.05)
    assert design["ratio_naoh"] == pytest.approx(14.5, abs=0.05)


def test_the_mixed_bed_run_is_within_its_operating_capacity(balance, design, streams):
    """DESIGN.md D-005: the salt of one run, in kmol (= keq for NaCl), uses at most half of the
    low-end operating capacity of either resin (SRC-4), the rest held for CO2 and silica."""
    salt_kg_h = streams["S12"]["flow"]["value"]
    salt_run = salt_kg_h / balance.M["NaCl"] * balance.RUN_MB
    assert salt_run == pytest.approx(design["salt_run_kmol"], rel=1e-4)
    assert salt_run == pytest.approx(0.284, abs=0.001)
    for cap, volume in ((balance.CAP_SBA[0], design["v_an"]), (balance.CAP_SAC[0], design["v_cat"])):
        assert salt_run / (cap * volume) <= balance.SALT_SHARE_MAX
    assert design["use_sba_low"] == pytest.approx(0.47, abs=0.005)
    assert balance.RUN_MB <= design["run_max"]
    text = _text("DESIGN.md")
    assert "0.284 kmol in a 36 h run" in text and "uses 47 %" in text


def test_the_pump_powers(balance, design, streams):
    rho = balance.RHO
    for sid, flow_sid, p_in, p_out in (
        ("E1", "S1", balance.P_ATM, balance.P_RAW_OUT),
        ("E2", "S3", balance.P_SUCTION, streams["S5"]["pressure"]["value"] / 100),
        ("E3", "S8", balance.P_ATM, balance.P_PRODUCT),
    ):
        flow = streams[flow_sid]["flow"]["value"]
        assert streams[sid]["duty"]["value"] == pytest.approx(flow / rho / 3600 * (p_out - p_in) * 100 / balance.ETA, rel=2e-3)
    assert streams["S5"]["pressure"]["value"] == pytest.approx(design["p_feed"] * 100, abs=0.1)


def test_the_neutralisation_heat_reaches_the_lci(streams):
    assert streams["E5"]["duty"]["provenance"] == "calculated"
    assert streams["E5"]["duty"]["value"] == pytest.approx(1.78, abs=0.01)
    keys = {f["key"] for f in _load("lca/lca.yaml")["flows"]}
    assert {"feed:RAW", "resource:H2O", "feed:HCL", "feed:NAOH", "feed:POWER", "product:WW", "product:AMBIENT"} <= keys


def test_the_lci_is_the_flowsheet_per_kg(streams):
    data = _load("lca/dataset.yaml")
    amounts = {e["key"]: e["amount"] for e in data["exchanges"]}
    product = amounts["product:DEMIN"]
    assert amounts["feed:RAW"] / product == pytest.approx(streams["S1"]["flow"]["value"] / streams["S11"]["flow"]["value"], rel=1e-6)
    assert amounts["product:WW"] == pytest.approx(streams["S18"]["flow"]["value"], rel=1e-6)
    assert amounts["resource:H2O"] == pytest.approx(streams["S1"]["flow"]["value"] * 0.9995, rel=1e-6)
    with (PROCESS / "lca" / "inventory.csv").open(encoding="utf-8") as fh:
        assert any("feed:HCL" in ",".join(row) for row in csv.reader(fh))
    lca = _load("lca/lca.yaml")
    raw = next(f for f in lca["flows"] if f["key"] == "feed:RAW")
    assert raw["resource"] is True
    water = next(f for f in lca["flows"] if f["key"] == "resource:H2O")
    assert water["elementary"]["flow"] == "water-river"


def test_the_library_links_exist():
    mappings = _load("lca/mappings.yaml")["exchanges"]
    for key, product in (("feed:HCL", "product:HCLACID"), ("feed:NAOH", "product:NAOH")):
        target = mappings[key]["dataset"]
        assert target["product"] == product
        data = yaml.safe_load((KIT / target["path"]).read_text(encoding="utf-8"))
        assert product in {e["key"] for e in data["exchanges"]}
    manifest = _load("process.yaml")
    keys = {f["inventory_key"]: f["chemical"] for group in manifest["chemistry"].values() for f in group if "inventory_key" in f}
    assert keys["product:DEMIN"] == "water/demineralised"
    assert keys["product:WW"] == "wastewater" and keys["feed:POWER"] == "electricity"
    # the wastewater is discharged, not treated: no utility-wwtp link, water and salt to water
    assert "product:WW" not in mappings
    flows = {f["key"]: f for f in _load("lca/lca.yaml")["flows"]}
    assert flows["product:WW"].get("emission") is True and "treatment" not in flows["product:WW"]
    assert flows["emission:H2O"]["elementary"] == {"compartment": "water", "subcompartment": "fresh-surface", "flow": "water-to-water"}
    assert flows["emission:NaCl"]["elementary"]["compartment"] == "water"


def test_the_grade_and_the_market_exist():
    registry = _load("chemicals/chemicals.yaml", KIT)
    water = next(c for c in registry["chemicals"] if c["slug"] == "water")
    assert "demineralised" in {g["slug"] for g in water["grades"]}
    market = next(m for m in _load("markets/water.yaml", KIT)["markets"] if m["product"] == "water/demineralised")
    (supplier,) = market["suppliers"]
    assert supplier["process"] == "demineralised-water-1"
    assert supplier["production_volume"]["value"] == pytest.approx(50000 * 8000 / 1000)


def test_equipment_list_names_every_linked_tag(sheet):
    tags = {e["tag"] for e in _load("equipment/equipment-list.yaml")["equipment"]}
    linked = {link["ref"] for s in sheet["steps"] for link in s.get("links", []) if link["target"] == "equipment"}
    assert linked <= tags


def test_published_public_with_cc_by():
    assert _load("process.yaml")["publication"] == {"status": "public", "license": "CC-BY-4.0"}


def test_requires_core_1_12():
    assert _load("plant.yaml")["requires"] == "cheme-as-code>=1.12"
