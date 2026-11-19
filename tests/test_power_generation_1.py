"""power-generation-1 (#469): the folder's stated numbers against its own flowsheet.

Fast and without core: the flowsheet, the LCI inventory and the manifest are read as YAML/CSV,
and the statements the folder makes in DESIGN.md, README.md and process.yaml are checked
against them:

- the electrical bus T901 closes: the net export Q11 is the gas turbines' calculated power Q1
  plus the steam turbine's Q3 less the auxiliary loads (D-010; core does not balance an
  energy-only step, L-3), and the auxiliaries are NETL's 13,562 kW;
- the net efficiencies (HHV and LHV) stated in DESIGN.md and process.yaml follow from Q11 and
  the fuel, and agree with NETL's 53.6 and 59.4 % to within 0.1 point;
- the calculated exhaust S3 is the stack gas S4 (the HRSG changes no composition) and matches
  NETL's stream 3;
- the water/steam loop closes at the HRSG, the steam turbine and the condenser;
- the gas turbines' loss Q2 is NETL's generator efficiency applied to NETL's 477 MW;
- the LCI's CO2 per kWh is the stack's and agrees with NETL's 342 kg/MWh net; the SCR
  consumables follow from NETL's 3.45 tons a day and the operating hours;
- the electricity and the natural gas carry no inventory_key (no default Atlas link);
- the process is public with CC-BY-4.0.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

import pytest
import yaml

KIT = Path(__file__).resolve().parents[1] / "processes" / "power-generation-1"

NETL_AUX_KW = 13_562.0
HHV_INPUT_KW = 1_354_905.0  # NETL Exhibit 5-9
LHV_INPUT_KW = 1_222_936.0
LHV_KJ_KG, HHV_KJ_KG = 47_201.0, 52_295.0  # NETL Exhibit 2-6


def _load(rel: str):
    return yaml.safe_load((KIT / rel).read_text())


@pytest.fixture(scope="module")
def sheet():
    return _load("process/flowsheet.yaml")


@pytest.fixture(scope="module")
def streams(sheet):
    return {s["id"]: s for s in sheet["streams"]}


def _state(streams, sid):
    return streams[sid]["state"]["design"]


def _duty(streams, qid):
    return _state(streams, qid)["duty"]["value"]


def _flow(streams, sid):
    return _state(streams, sid)["flow"]["value"]


def test_the_bus_closes(streams):
    q1 = _duty(streams, "Q1")
    assert _state(streams, "Q1")["duty"]["provenance"] == "calculated"
    gross = q1 + _duty(streams, "Q3")
    aux = sum(_duty(streams, q) for q in ("Q6", "Q7", "Q8", "Q9", "Q10"))
    assert aux == pytest.approx(NETL_AUX_KW, abs=0.01)
    assert _duty(streams, "Q11") == pytest.approx(gross - aux, abs=0.1)
    assert _duty(streams, "Q11") == pytest.approx(727_000.0, rel=0.005)


def test_the_net_efficiencies_follow_from_the_flowsheet(streams):
    net = _duty(streams, "Q11")
    fuel = _flow(streams, "S2")
    hhv = net / (fuel * HHV_KJ_KG / 3600.0)
    lhv = net / LHV_INPUT_KW
    assert hhv == pytest.approx(net / HHV_INPUT_KW, rel=1e-4)
    assert abs(hhv * 100 - 53.6) < 0.1 and abs(lhv * 100 - 59.4) < 0.1
    design = (KIT / "DESIGN.md").read_text()
    manifest = (KIT / "process.yaml").read_text()
    for text in (design, manifest):
        assert f"{hhv * 100:.2f} %" in text
        assert f"{lhv * 100:.2f} %" in text
    assert f"{net / 1000:.1f} MW" in manifest
    heat_rate = HHV_INPUT_KW / net * 3600.0
    assert f"{heat_rate:,.0f} kJ" in (KIT / "README.md").read_text()


def test_the_gas_turbine_loss_is_netls_generator_efficiency(streams):
    assert _duty(streams, "Q2") == pytest.approx(477_000.0 * (1 / 0.985 - 1), abs=0.1)
    shaft = _duty(streams, "Q1") + _duty(streams, "Q2")
    assert shaft == pytest.approx(477_000.0 / 0.985, rel=0.002)


def test_the_exhaust_is_the_stack_gas_and_netls_stream_3(streams):
    s3, s4 = _state(streams, "S3"), _state(streams, "S4")
    assert s3["flow"]["provenance"] == "calculated"
    # core writes the calculated flow to six significant figures
    assert s4["flow"]["value"] == pytest.approx(s3["flow"]["value"], rel=1e-6)
    netl = {"Ar": 0.0089, "CO2": 0.0408, "H2O": 0.0875, "N2": 0.7428, "O2": 0.1200}
    y3 = s3["composition"]["values"]
    y4 = s4["composition"]["values"]
    for comp, value in netl.items():
        assert y4[comp] == pytest.approx(y3[comp], abs=1e-6)
        assert y3[comp] == pytest.approx(value, abs=1e-4)
    for fuel in ("CH4", "C2H6", "C3H8", "C4H10"):
        assert y3.get(fuel, 0.0) == 0.0


def test_the_water_steam_loop_closes(streams):
    f = {s: _flow(streams, s) for s in ("S5", "S6", "S7", "S9", "S10", "S11", "S12", "S13", "S14")}
    assert f["S5"] + f["S7"] + f["S9"] == pytest.approx(f["S6"] + f["S12"], abs=0.1)
    assert f["S10"] == pytest.approx(f["S7"] + f["S9"], abs=0.1)
    assert f["S10"] + f["S13"] == pytest.approx(f["S11"] + f["S14"], abs=0.1)
    assert f["S11"] == f["S12"]
    ct = {s: _flow(streams, s) for s in ("S20", "S21", "S22")}
    assert ct["S20"] == pytest.approx(ct["S21"] + ct["S22"], abs=0.1)


def _inventory():
    with (KIT / "lca" / "inventory.csv").open() as f:
        return {row["key"]: row for row in csv.DictReader(f)}


def test_the_lci_co2_and_the_scr_consumables():
    inv = _inventory()
    co2 = float(inv["emission:CO2"]["quantity"])
    assert co2 == pytest.approx(0.342, rel=0.01)  # NETL Exhibit 5-11: 342 kg/MWh net
    assert f"{co2:.4f} kg/kWh" in (KIT / "process.yaml").read_text()
    lca = _load("lca/lca.yaml")
    hours = lca["operation"]["hours_per_year"]
    assert hours == round(8760 * 0.85)
    solution_per_day = 3.45 * 907.18474
    cons = {c["id"]: c for c in lca["consumables"]}
    assert cons["scr-ammonia"]["per_year"] == pytest.approx(solution_per_day * 0.19 * hours / 24, abs=1)
    assert cons["scr-dilution-water"]["per_year"] == pytest.approx(solution_per_day * 0.81 * hours / 24, abs=1)
    est = lca["emission_estimates"][0]
    gj = 93_272.0 * HHV_KJ_KG / 1e6
    assert est["activity"]["value"] == pytest.approx(gj, abs=0.01)
    for subst, t_a in (("NOx", 56), ("CO", 29), ("SO2", 15), ("PM", 29)):
        assert est["factors"][subst]["value"] == pytest.approx(t_a * 1e6 / hours / gj, rel=1e-3)


def test_no_default_atlas_link_for_electricity_or_gas():
    manifest = _load("process.yaml")
    rows = manifest["chemistry"]["inputs"] + manifest["chemistry"]["outputs"]
    for row in rows:
        if row["chemical"].startswith("electricity") or row["chemical"] == "methane":
            assert "inventory_key" not in row
    mappings = _load("lca/mappings.yaml")["exchanges"]
    assert mappings["feed:NG"]["atlas"] is False


def test_published_public_with_cc_by():
    manifest = _load("process.yaml")
    assert manifest["publication"] == {"status": "public", "license": "CC-BY-4.0"}
    assert re.search(r"requires: cheme-as-code>=1\.12", (KIT / "plant.yaml").read_text())
