"""The library utilities (processes/utility-*, process-library#45): their datasets load, close
their mass, element and energy balances, build into the LCI export without findings, link one
another inside the Atlas, and refuse a link outside their operating range."""

from __future__ import annotations

import json
import math
import shutil
import sys
from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")
pytest.importorskip("openpyxl")

KIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KIT / "scripts"))

import build_lci  # noqa: E402

UTILITIES = sorted(p.parent.name for p in (KIT / "processes").glob("utility-*/process.yaml"))
DATASETS = {pid: sorted((KIT / "processes" / pid / "lca" / "datasets").glob("*.yaml")) for pid in UTILITIES}
DB = "cheme-as-code-atlas-0.1.0"
WATER_RESOURCE = "831f249e-53f2-49cf-a93c-7cee105f048e"
# kg exchanges deliberately outside the element balance (generation.balance.outside): the reference
# flow of the service (gas flared, water treated, air delivered), which the balance does not
# follow through the unit, and COD, which is an oxygen demand rather than a substance.
OUTSIDE_BY_DESIGN = {
    "utility-flare": {"product:flare-gas"},
    "utility-instrument-air": {"product:instrument-air"},
    "utility-wwtp": {"product:wastewater", "emission:COD"},
}


def _load(pid: str) -> dict:
    (path,) = DATASETS[pid]
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _amounts(data: dict) -> dict[str, float]:
    return {e["key"]: e["amount"] for e in data["exchanges"]}


def _params(data: dict) -> dict[str, float]:
    return {p["name"]: p["value"] for p in data["parameters"]}


def test_the_utility_family_is_there() -> None:
    assert UTILITIES == [
        "utility-chiller", "utility-cooling-tower", "utility-flare", "utility-instrument-air", "utility-steam-ng-boiler", "utility-wwtp",
    ]
    assert all(len(files) == 1 for files in DATASETS.values()), DATASETS


@pytest.mark.parametrize("pid", UTILITIES)
def test_every_parameter_has_a_source_and_every_assumption_a_todo(pid: str) -> None:
    for parameter in _load(pid)["parameters"]:
        assert parameter["source"], parameter
        if parameter["source"].startswith("ASSUMED"):
            assert "TODO" in parameter["source"], parameter


@pytest.mark.parametrize("pid", UTILITIES)
def test_the_dataset_loads_in_core_and_its_tier_checks_pass(pid: str) -> None:
    schemas = pytest.importorskip("chemeascode.domains.assessment.lca.schemas")
    estimate = pytest.importorskip("chemeascode.domains.assessment.lca.estimate")
    balance = pytest.importorskip("chemeascode.domains.assessment.lca.balance")
    data = _load(pid)
    dataset = schemas.LciDataset.model_validate(data)  # re-evaluates every formula against its amount
    assert all(e.formula for e in dataset.exchanges), "every amount is a formula of the parameters"
    maturity = yaml.safe_load((KIT / "processes" / pid / "process.yaml").read_text())["maturity"]
    findings = [f for f in estimate.tier_findings(dataset, pid, maturity) if f.level != "info"]
    # core warns (cheme.lci-mass-outside-balance) for kg exchanges outside the element balance.
    # Only the reference flow of a treatment or supply service and COD (an oxygen demand, not a
    # substance) are outside by design; any other exchange outside the balance still fails.
    outside = [f for f in findings if f.rule == "cheme.lci-mass-outside-balance"]
    for finding in outside:
        named = set(finding.message.rsplit(": ", 1)[1].split(", "))
        assert named <= OUTSIDE_BY_DESIGN.get(pid, set()), finding
    assert [f for f in findings if f not in outside] == []
    if dataset.generation is not None:
        found = balance.element_balance(dataset)
        assert found.closed, found.unbalanced()
        assert found.record().model_dump() == data["generation"]["balance"]


# --- balances, checked independently of core ----------------------------------------------


def test_steam_boiler_energy_water_and_carbon_balances() -> None:
    data = _load("utility-steam-ng-boiler")
    a, p = _amounts(data), _params(data)
    assert a["feed:feedwater"] == pytest.approx(a["product:steam"] + a["output:blowdown"])
    assert a["output:blowdown"] / a["feed:feedwater"] == pytest.approx(p["blowdown"])
    heat = a["product:steam"] * (p["h_g"] - p["h_mu"]) + a["output:blowdown"] * (p["h_f"] - p["h_mu"])
    assert a["feed:natural-gas"] * p["lhv"] * p["eta"] == pytest.approx(heat)
    assert a["emission:CO2"] / a["feed:natural-gas"] == pytest.approx(44.009 / 16.043)  # CH4 + 2 O2 -> CO2 + 2 H2O
    assert a["emission:H2O"] / a["feed:natural-gas"] == pytest.approx(2 * 18.015 / 16.043)
    assert 2.6 < heat / 1000 / a["product:steam"] < 2.8  # MJ/kg: saturated steam at 11 bar(a) from 15 degC water
    product = next(e for e in data["exchanges"] if e["key"] == "product:steam")
    assert product["carrier"]["kind"] == "steam" and product["carrier"]["pressure"] == 11.0


def test_cooling_tower_water_balance_and_latent_heat() -> None:
    data = _load("utility-cooling-tower")
    a, p = _amounts(data), _params(data)
    makeup = a["resource:water"]
    assert makeup == pytest.approx(a["emission:H2O-evaporation"] + a["emission:H2O-drift"] + a["output:blowdown"])
    assert makeup / (a["output:blowdown"] + a["emission:H2O-drift"]) == pytest.approx(p["cycles"])
    # evaporation can carry no more than the heat rejected: about 2.43 MJ/kg latent heat near 30 degC
    # (h_g - h_f of water at 30 degC, IAPWS-95), so at most ~1.48 kg/kWh; the rest leaves as sensible heat
    evaporated = a["emission:H2O-evaporation"] / a["product:heat-rejected"]
    assert 0.9 < evaporated < 3600 / 2430
    product = next(e for e in data["exchanges"] if e["key"] == "product:heat-rejected")
    assert product["carrier"] == {**product["carrier"], "kind": "cold", "temperature": 25.0}


def test_wwtp_cod_and_carbon_balances() -> None:
    data = _load("utility-wwtp")
    a, p = _amounts(data), _params(data)
    removed = p["cod_in"] * p["removal"]
    biomass_cod = a["output:sludge"] * p["cod_bio"]
    assert a["feed:O2"] + biomass_cod == pytest.approx(removed)  # COD removed = O2 used + COD of biomass grown
    assert a["emission:COD"] == pytest.approx(p["cod_in"] - removed)
    carbon_in = a["feed:organics"] * 12.011 / 30.026
    carbon_out = a["emission:CO2"] * 12.011 / 44.009 + a["output:sludge"] * 5 * 12.011 / 113.116
    assert carbon_in == pytest.approx(carbon_out)


def test_flare_stoichiometry() -> None:
    a, p = _amounts(_load("utility-flare")), _params(_load("utility-flare"))
    assert a["emission:CH4"] == pytest.approx(a["feed:gas"] * (1 - p["eta"]))
    assert a["emission:CO2"] == pytest.approx(a["feed:gas"] * p["eta"] * 44.009 / 16.043)


def test_chiller_first_law_and_cop() -> None:
    data = _load("utility-chiller")
    a, p = _amounts(data), _params(data)
    assert a["output:heat-rejected"] == pytest.approx(a["product:cold"] + a["feed:electricity"])
    carnot = (p["t_evap"] + 273.15) / (p["t_cond"] - p["t_evap"])
    assert a["product:cold"] / a["feed:electricity"] == pytest.approx(p["carnot_fraction"] * carnot)
    assert "generation" not in data  # no material flow: no element balance, so no Tier 1 block
    assert any("refrigerant" in x for x in data["system_boundary"]["excluded"])


def test_instrument_air_moisture_balance_and_isothermal_work() -> None:
    data = _load("utility-instrument-air")
    a, p = _amounts(data), _params(data)
    assert a["feed:moisture"] == pytest.approx(a["output:condensate"] + a["emission:H2O"])
    compressed = a["product:instrument-air"] / (1 - p["purge"])
    work = compressed * (1 / p["M_air"] + p["w1"] / p["M_H2O"]) * p["R"] * p["t1"] * math.log(p["p2"] / p["p1"]) / p["eta_iso"] / 3600
    assert a["feed:electricity"] == pytest.approx(work)


# --- the export --------------------------------------------------------------------------------


def _library(tmp: Path, consumer: dict | None = None, mappings_change=None) -> Path:
    """The utilities and ASU-1 (its dataset only) with the real registry and mappings, plus an
    optional synthetic manifest-only consumer."""
    library = tmp / "library"
    for folder in ("chemicals", "lci", "taxonomy"):
        shutil.copytree(KIT / folder, library / folder)
    for pid in UTILITIES:
        shutil.copytree(KIT / "processes" / pid, library / "processes" / pid)
    (library / "processes" / "asu-1" / "lca").mkdir(parents=True)
    shutil.copy(KIT / "processes" / "asu-1" / "process.yaml", library / "processes" / "asu-1")
    shutil.copy(KIT / "processes" / "asu-1" / "lca" / "dataset.yaml", library / "processes" / "asu-1" / "lca")
    if consumer is not None:
        folder = library / "processes" / "test-consumer"
        (folder / "lca" / "datasets").mkdir(parents=True)
        (folder / "process.yaml").write_text(yaml.safe_dump({
            "schema": "cheme-as-code/process/v1", "id": "test-consumer", "title": "Test consumer", "summary": "synthetic",
            "families": ["utilities"], "maturity": "concept", "validation": {"status": "unreviewed"},
            "chemistry": {"inputs": [{"chemical": "steam", "role": "utility", "inventory_key": "feed:steam"}, {"chemical": "nitrogen/gan-8barg-10ppm", "role": "utility", "inventory_key": "feed:nitrogen"}],
                          "outputs": [{"chemical": "hydrogen", "role": "main-product", "inventory_key": "product:x"}]},
        }))
        (folder / "lca" / "datasets" / "consumer.yaml").write_text(yaml.safe_dump(consumer, sort_keys=False))
    if mappings_change is not None:
        path = library / "lci" / "mappings.yaml"
        data = yaml.safe_load(path.read_text())
        mappings_change(data)
        path.write_text(yaml.safe_dump(data, sort_keys=False))
    return library


def _consumer(steam: dict) -> dict:
    return {
        "schema": "cheme/lci_dataset/v2", "kind": "lci_dataset", "id": "consumer", "title": "Test consumer", "basis": "1 kg",
        "exchanges": [
            {"key": "product:x", "title": "Product", "type": "product", "amount": 1.0, "unit": "kg"},
            {"key": "feed:steam", "title": "Steam", "type": "input", "amount": 2.0, "unit": "kg", **steam},
            {"key": "feed:nitrogen", "title": "Nitrogen", "type": "input", "amount": 0.5, "unit": "kg"},
        ],
    }


def _build(library: Path, tmp: Path) -> build_lci.Report:
    return build_lci.build(library, tmp / "out", "0.1.0", commit="test")


def _activities(tmp: Path) -> dict[str, dict]:
    return build_lci.read_workbook(tmp / "out" / "lci" / f"{DB}.xlsx")


def _exchange(activity: dict, key: str) -> dict:
    return next(e for e in activity["exchanges"] if e.get("atlas key") == key)


def test_the_library_builds_strict_with_the_utilities(tmp_path: Path) -> None:
    report = build_lci.build(KIT, tmp_path / "out", "0.1.0", commit="test")
    assert (report.errors, report.warnings) == ([], [])
    variant = build_lci.build(KIT, tmp_path / "substitution", "0.1.0", commit="test", system_model="substitution")
    assert (variant.errors, variant.warnings) == ([], [])
    package = json.loads((tmp_path / "out" / "lci" / "datapackage.json").read_text())
    built = {p["id"] for p in package["processes"]}
    assert set(UTILITIES) <= built
    steam = next(a for p in package["processes"] if p["id"] == "utility-steam-ng-boiler" for a in p["activities"])
    assert (steam["chemical"], steam["grade"], steam["carrier"]["pressure"]) == ("steam", "mp-11bara", 11.0)


def test_utilities_link_one_another_inside_the_atlas_and_asu_1_stays_on_its_proxy(tmp_path: Path) -> None:
    assert _build(_library(tmp_path), tmp_path).errors == []
    acts = _activities(tmp_path)
    wwtp = "Wastewater treatment, activated sludge"
    tower = "Cooling water, evaporative cooling tower, 25/35 degC"
    links = {
        ("utility-steam-ng-boiler:steam-mp-11bara-natural-gas-boiler:product:steam", "output:blowdown"): wwtp,
        ("utility-cooling-tower:cooling-tower-evaporative-25-35:product:heat-rejected", "output:blowdown"): wwtp,
        ("utility-chiller:chiller-chilled-water-6c:product:cold", "output:heat-rejected"): tower,
        ("utility-instrument-air:instrument-air-8bara-dried:product:instrument-air", "output:heat-rejected"): tower,
        ("utility-instrument-air:instrument-air-8bara-dried:product:instrument-air", "output:condensate"): wwtp,
    }
    for (code, key), name in links.items():
        exchange = _exchange(acts[code], key)
        assert exchange["atlas activity"] == name, (code, key)
        assert exchange["database"] == DB  # the background alternative: a unit proxy or the screening proxy
    # the water resource of the cooling tower is in the export, by its biosphere3 UUID, in m3
    water = _exchange(acts["utility-cooling-tower:cooling-tower-evaporative-25-35:product:heat-rejected"], "resource:water")
    assert (water["atlas flow uuid"], water["unit"]) == (WATER_RESOURCE, "cubic meter")
    assert water["amount"] == pytest.approx(_amounts(_load("utility-cooling-tower"))["resource:water"] / 1000 * 0.001)
    # ASU-1's heat rejected keeps the screening proxy (atlas: false) until ASU-1 decides its cooling (#77)
    asu = _exchange(acts["asu-1:asu-1-500-t-d-gox:product:GOXP"], "product:CW")
    assert "atlas activity" not in asu and asu["name"].startswith("cooling water service")


def test_without_the_override_asu_1_links_the_cooling_tower(tmp_path: Path) -> None:
    library = _library(tmp_path, mappings_change=lambda m: m["exchanges"].pop("asu-1/product:CW"))
    assert _build(library, tmp_path).errors == []
    asu = _exchange(_activities(tmp_path)["asu-1:asu-1-500-t-d-gox:product:GOXP"], "product:CW")
    assert asu["atlas activity"] == "Cooling water, evaporative cooling tower, 25/35 degC"


@pytest.mark.parametrize(
    ("need", "supply", "refused"),
    [
        ({"kind": "steam", "pressure": 5.0}, {"kind": "steam", "pressure": 11.0}, False),
        ({"kind": "steam", "pressure": 40.0}, {"kind": "steam", "pressure": 11.0}, True),
        ({"kind": "heat", "temperature": 150.0}, {"kind": "steam", "pressure": 11.0, "temperature": 184.06}, False),
        ({"kind": "heat", "temperature": 250.0}, {"kind": "steam", "pressure": 11.0, "temperature": 184.06}, True),
        ({"kind": "cold", "temperature": 30.0}, {"kind": "cold", "temperature": 25.0}, False),
        ({"kind": "cold", "temperature": 10.0}, {"kind": "cold", "temperature": 25.0}, True),
        ({"kind": "electricity"}, {"kind": "steam", "pressure": 11.0}, True),
        (None, {"kind": "steam", "pressure": 11.0}, False),
    ],
)
def test_carrier_refusal(need, supply, refused: bool) -> None:
    assert bool(build_lci.carrier_refusal(need, supply)) is refused


def test_a_consumer_in_range_links_the_utility_and_asu_1_nitrogen(tmp_path: Path) -> None:
    consumer = _consumer({"carrier": {"kind": "steam", "pressure": 6.0, "level": "LP"}})
    report = _build(_library(tmp_path, consumer), tmp_path)
    assert (report.errors, report.warnings) == ([], [])
    activity = _activities(tmp_path)["test-consumer:consumer:product:x"]
    steam = _exchange(activity, "feed:steam")
    assert steam["atlas activity"] == "Steam generation, natural-gas boiler, saturated 11 bar(a)"
    assert steam["name"].startswith("steam, saturated, 11 bar(a), per kg")  # the background alternative (unit proxy)
    nitrogen = _exchange(activity, "feed:nitrogen")
    assert nitrogen["atlas activity"] == "Cryogenic air separation unit (500 t/d GOX)"
    assert nitrogen["atlas reference product"] == "Nitrogen, gaseous, <= 10 ppm O2, 8 barg"  # the grade it names
    assert nitrogen["name"] == "market for nitrogen, liquid"


def test_a_consumer_outside_the_range_is_refused(tmp_path: Path) -> None:
    consumer = _consumer({"carrier": {"kind": "steam", "pressure": 40.0, "level": "HP"}})
    report = _build(_library(tmp_path, consumer), tmp_path)
    assert report.errors == []
    assert any("feed:steam" in w and "outside its operating range" in w and "40 bar(a)" in w for w in report.warnings), report.warnings
    steam = _exchange(_activities(tmp_path)["test-consumer:consumer:product:x"], "feed:steam")
    assert "atlas activity" not in steam


def test_an_explicit_link_outside_the_range_is_an_error(tmp_path: Path) -> None:
    link = {"dataset": {"path": "processes/utility-steam-ng-boiler/lca/datasets/steam-mp-11bara-natural-gas-boiler.yaml", "product": "steam"}}
    consumer = _consumer({"carrier": {"kind": "steam", "pressure": 40.0}, "link": link})
    errors = _build(_library(tmp_path, consumer), tmp_path).errors
    assert any("feed:steam" in e and "outside its operating range" in e for e in errors), errors
    consumer = _consumer({"carrier": {"kind": "steam", "pressure": 6.0}, "link": link})
    assert _build(_library(tmp_path / "ok", consumer), tmp_path / "ok").errors == []
