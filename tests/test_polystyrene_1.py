"""polystyrene-1 (#467): the folder's stated numbers against its own flowsheet.

Fast, without core where it can be: the flowsheet's streams (propagated by core, some values
given by scripts/ps_balance.py) are read as YAML, and the statements the folder makes in
DESIGN.md, README.md and process.yaml are checked against them:

- the specific styrene (1.006 kg/kg) follows from S1 and S14 and lies inside the POL BREF range
  recorded in benchmarks/polymers.yaml;
- the specs hold: 100 kt/a of polystyrene in 8000 h, 7 wt% ethylbenzene in the reactor feed, the
  purge fraction 0.01366 of the condensate;
- the conversions per pass (0.35, 0.615) and over the train (0.75), the solution's 69.7 wt%
  polymer, the residual volatiles (about 520 ppm) and the vent's 86 g/t;
- the reactors' duties are their heat of reaction and sensible heats plus the agitators' power;
- the adiabatic rises of D-010 follow from the styrene left in S4 and S5;
- the balance script re-solves the same plant (with thermo, as in core's environment);
- every heat and power stream reaches the LCI, which links the styrene to styrene-1;
- the benchmark binding names both KPIs; the process is public with CC-BY-4.0.
"""

from __future__ import annotations

import csv
import importlib.util
from pathlib import Path

import pytest
import yaml

KIT = Path(__file__).resolve().parents[1]
PROCESS = KIT / "processes" / "polystyrene-1"
MW = {"STY": 104.152, "EB": 106.168, "PS": 104.152, "H2O": 18.015}


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


def _kg(streams: dict, sid: str) -> dict[str, float]:
    """Component mass flows, kg/h, of a stream with a mass flow and a mole or mass composition."""
    state = streams[sid]
    flow = state["flow"]["value"]
    comp = state["composition"]
    values = comp["values"]
    if comp["basis"] == "mass_fraction":
        return {k: flow * v for k, v in values.items()}
    mass = {k: v * MW[k] for k, v in values.items()}
    total = sum(mass.values())
    return {k: flow * m / total for k, m in mass.items()}


def _duty(streams: dict, sid: str) -> float:
    return streams[sid]["duty"]["value"]


def test_specific_styrene_and_the_specs(streams):
    s1, s3, s14 = _kg(streams, "S1"), _kg(streams, "S3"), _kg(streams, "S14")
    assert s14["PS"] * 8000 / 1000 == pytest.approx(100_000, rel=1e-4)
    assert s3["EB"] / sum(s3.values()) == pytest.approx(0.07, abs=1e-5)
    styrene = sum(s1.values()) / sum(s14.values())
    assert round(styrene, 3) == 1.006
    bench = _load("benchmarks/polymers.yaml", KIT)
    low, high = bench["kpis"]["gpps-specific-styrene"]["references"][0]["range"]
    assert low <= styrene <= high
    assert "1.006 kg" in _text("process.yaml") and "1.006 kg" in _text("README.md")
    purge = streams["S20"]["flow"]["value"] / streams["S19"]["flow"]["value"]
    assert purge == pytest.approx(0.01366, abs=5e-6)
    assert "0.01366" in _text("DESIGN.md")
    assert streams["S20"]["flow"]["value"] == pytest.approx(74.0, abs=0.05)


def test_conversions_solution_residual_and_vent(sheet, streams):
    steps = {s["id"]: s for s in sheet["steps"]}
    assert steps["R101"]["conversion"] == {"POLY": 0.35}
    assert steps["R102"]["conversion"] == {"POLY": 0.615}
    s3, s4, s5 = _kg(streams, "S3"), _kg(streams, "S4"), _kg(streams, "S5")
    assert 1 - s4["STY"] / s3["STY"] == pytest.approx(0.35, abs=1e-5)
    # 1 - 0.65 x 0.385 = 0.74975, stated as 0.75
    assert 1 - s5["STY"] / s3["STY"] == pytest.approx(1 - 0.65 * 0.385, abs=1e-5)
    assert s5["PS"] / sum(s5.values()) == pytest.approx(0.697, abs=5e-4)
    s14 = _kg(streams, "S14")
    ppm = 1e6 * (s14["STY"] + s14["EB"]) / sum(s14.values())
    assert 500 <= ppm <= 540
    vent = 1e6 * streams["S18"]["flow"]["value"] / s14["PS"]  # g per t
    assert vent == pytest.approx(86, abs=1)


def test_reactor_duties_are_reaction_and_sensible_heat_plus_power(streams):
    mat = {c["id"]: c for c in _load("process/materials.yaml")["components"]}
    rxn = _load("process/reactions.yaml")["reactions"][0]
    dhr = rxn["heat_of_reaction"]["value"]  # kJ/kmol at 298.15 K
    assert dhr == pytest.approx(-710 * 104.152, abs=1)

    def heat(sin, sout, tin, tout, power):
        a, b = _kg(streams, sin), _kg(streams, sout)
        cp = lambda s: sum(m / MW[k] * mat[k]["liquid_heat_capacity"] for k, m in s.items())  # noqa: E731
        made = (b["PS"] - a["PS"]) / MW["PS"]
        h = made * dhr + cp(a) * (298.15 - tin) + cp(b) * (tout - 298.15)
        return -(h / 3600) + power  # heat removed, kW

    t3, t4, t5 = (streams[s]["temperature"]["value"] for s in ("S3", "S4", "S5"))
    assert heat("S3", "S4", t3, t4, _duty(streams, "P1")) == pytest.approx(_duty(streams, "Q1"), rel=1e-3)
    assert heat("S4", "S5", t4, t5, _duty(streams, "P2")) == pytest.approx(_duty(streams, "Q2"), rel=1e-3)


def test_adiabatic_rises_of_design_d010(streams):
    for sid, stated in (("S4", 246), ("S5", 95)):
        s = _kg(streams, sid)
        rise = s["STY"] / sum(s.values()) * 710 / (182.0 / 104.152)
        assert round(rise) == stated
        assert f"{stated} K" in _text("DESIGN.md")


def test_balance_script_resolves_the_same_plant(streams):
    pytest.importorskip("scipy")
    pytest.importorskip("thermo")
    spec = importlib.util.spec_from_file_location("ps_balance", PROCESS / "scripts" / "ps_balance.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    from scipy.optimize import fsolve

    fresh, purge = fsolve(module.residuals, [12600.0, 0.015], xtol=1e-12)
    assert fresh == pytest.approx(streams["S1"]["flow"]["value"], abs=0.1)
    assert purge == pytest.approx(0.01366, abs=5e-6)


def test_every_energy_stream_reaches_the_lci(streams):
    rows = {r["key"]: r for r in csv.DictReader((PROCESS / "lca" / "inventory.csv").open(encoding="utf-8"))}
    cw = sum(_duty(streams, q) for q in ("Q1", "Q2", "Q4", "Q5"))
    assert float(rows["product:CW"]["plant"]) == pytest.approx(cw, rel=1e-4)
    power = sum(_duty(streams, p) for p in ("P1", "P2", "P3", "P4", "P5"))
    assert power == 660
    assert float(rows["feed:POWER"]["plant"]) == pytest.approx(power)
    assert float(rows["feed:HOTOIL"]["plant"]) == pytest.approx(_duty(streams, "Q3"))
    nitrogen = float(rows["consumable:nitrogen"]["quantity"])
    assert nitrogen == pytest.approx(0.022, abs=2e-4)
    mappings = _load("lca/mappings.yaml")["exchanges"]
    link = mappings["feed:SM"]["dataset"]
    dataset = _load(link["path"], KIT)
    assert link["product"] in {e["key"] for e in dataset["exchanges"]}


def test_benchmark_binding_and_publication():
    bench = _load("benchmarks/polymers.yaml", KIT)
    binding = next(d for d in bench["datasets"] if d["process"] == "polystyrene-1")
    assert set(binding["kpis"]) == {"gpps-specific-styrene", "gpps-specific-energy"}
    dataset = _load("lca/dataset.yaml")
    assert binding["dataset"] == dataset["id"]
    manifest = _load("process.yaml")
    assert manifest["publication"] == {"status": "public", "license": "CC-BY-4.0"}
    assert "polymers" in manifest["families"]
    assert _load("plant.yaml")["requires"] == "cheme-as-code>=1.12"
