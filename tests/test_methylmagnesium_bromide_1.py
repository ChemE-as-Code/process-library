"""methylmagnesium-bromide-1 (#157): the folder's stated numbers against its own files.

Fast, mostly without core: the statements the folder makes in comments, in the equipment list
and in DESIGN.md are checked against the values its YAML files hold (review of
process-library#383, and of the move to core 1.9.0):

- the LCA dataset and manifest name the hashes of the input files as they are committed (the
  dataset went stale when process.yaml was edited after the last ``cheme assess lca --write``);
- the product's heat capacity in materials.yaml and DESIGN.md D-006 is what the declared liquid
  heat capacities and S9's composition give (1.58 kJ/(kg K), once stated as 1.66), and methyl
  bromide's 71.0 kJ/(kmol K) is thermo's value at 318 K, not at 298 K;
- E-101's duty during the dosing is the batch's vaporiser energy over the dosing segments that
  carry gas (once stated as 15 kW over a 6.75 h that no recipe interval has);
- D-011 names the toxic methyl bromide a cooling failure releases, in amounts that follow from
  the accumulation and the dose, and D-007 the hydrogen from quenching the magnesium cake;
- core 1.9.0 (ADR 0058): no hand-set ``hazard.mtt``; the default MTT, 2-MeTHF's boiling point at
  S3's pressure by Clausius-Clapeyron from its declared heat of vaporization, is the 356.3 K
  D-011 states; the warm-up's hot water lies above the solvent's normal boiling point (the MTT
  once the pad is lost) and 3.2 K below the MTT at 120 kPa(a), stated with its safeguard in D-010;
- core 1.9.0 (ADR 0059): R101's model writes Q1 (``energy_port: q``, ``calculated``), the
  charge's warm-up Q2 stays a typed hand value, and both are in the LCI (brine and LP steam);
- core 1.9.0 (ADR 0058): R-101's vent capacity, 20 m3/h ASSUMED, against D-011's gas release at
  the MTSR: within it at the base rate and k/10, exceeded at k/100 and uninitiated (the design
  finding); with core importable, the screening's own MTT and gas release are compared too.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
from pathlib import Path

import pytest
import yaml

KIT = Path(__file__).resolve().parents[1]
PROCESS = KIT / "processes" / "methylmagnesium-bromide-1"

#: m3(STP)/kmol at 273.15 K and 101.325 kPa
NM3_PER_KMOL = 22.414


def _yaml(rel: str):
    return yaml.safe_load((PROCESS / rel).read_text(encoding="utf-8"))


def _text(rel: str) -> str:
    return " ".join((PROCESS / rel).read_text(encoding="utf-8").replace("#", " ").split())


def _section(decision: str) -> str:
    """One DESIGN.md decision, whitespace collapsed."""
    text = (PROCESS / "DESIGN.md").read_text(encoding="utf-8")
    m = re.search(rf"^## {decision} .*?(?=^## )", text, flags=re.S | re.M)
    assert m, f"DESIGN.md has no {decision}"
    return " ".join(m.group(0).split())


def _sha256(rel: str) -> str:
    return "sha256:" + hashlib.sha256((PROCESS / rel).read_bytes()).hexdigest()


@pytest.fixture(scope="module")
def model():
    materials = _yaml("process/materials.yaml")
    flowsheet = _yaml("process/flowsheet.yaml")
    recipe = _yaml("process/recipe.yaml")
    comps = {c["id"]: c for c in materials["components"]}
    streams = {s["id"]: s for s in flowsheet["streams"]}
    steps = {s["id"]: s for s in flowsheet["steps"]}
    design = (PROCESS / "DESIGN.md").read_text(encoding="utf-8")
    batches = float(re.search(r"cycle [\d.]+ h, ([\d.]+) batches in", " ".join(design.split())).group(1))
    hours = recipe["hours_per_year"]["value"]
    return {"comps": comps, "streams": streams, "steps": steps, "recipe": recipe,
            "cycle": hours / batches}


def _composition(model, sid: str) -> dict[str, float]:
    return model["streams"][sid]["state"]["design"]["composition"]["values"]


def _mass_cp(model, sid: str) -> float:
    """kJ/(kg K) of a stream from the declared liquid heat capacities (ideal mixing)."""
    x = _composition(model, sid)
    comps = model["comps"]
    cp = sum(v * comps[c].get("liquid_heat_capacity", 0.0) for c, v in x.items())
    mm = sum(v * comps[c]["molar_mass"] for c, v in x.items())
    return cp / mm


def _per_batch_kg(model, sid: str) -> float:
    return model["streams"][sid]["state"]["design"]["flow"]["value"] * model["cycle"]


def test_lca_dataset_and_manifest_name_the_committed_inputs():
    """`cheme assess lca --check` fails when an input changed after the last --write."""
    dataset = _yaml("lca/dataset.yaml")
    manifest = json.loads((PROCESS / "lca" / "manifest.json").read_text(encoding="utf-8"))
    recorded = {**dataset["provenance"]["files"], **manifest["inputs"]}
    assert "process.yaml" in recorded
    stale = {rel: h for rel, h in recorded.items() if _sha256(rel) != h}
    assert not stale, f"rerun cheme assess lca --write: stale input hashes {sorted(stale)}"


@pytest.mark.parametrize("rel", ["process/materials.yaml", "DESIGN.md"])
def test_product_heat_capacity_statement_matches_the_declared_data(rel, model):
    text = _text(rel)
    m = re.search(r"product's heat capacity is then ([\d.]+) kJ/\(kg K\)", text)
    assert m, f"{rel}: no statement of the product's heat capacity"
    stated = float(m.group(1))
    for sid in ("S9", "S6"):
        assert abs(stated - _mass_cp(model, sid)) < 0.006, (rel, sid, stated, _mass_cp(model, sid))


def test_methyl_bromide_heat_capacity_temperature():
    """thermo: 67.1 kJ/(kmol K) at 298.15 K, 71.0 at 318.15 K."""
    text = _text("process/materials.yaml")
    assert "318 K and 298 K" not in text
    assert re.search(r"methyl bromide 71\.0 \(thermo, both at 318 K", text)


def test_e101_duty_over_the_gas_flow(model):
    q3 = next(s for s in model["streams"].values() if s["id"] == "Q3")
    kw_avg = q3["state"]["design"]["duty"]["value"]
    kwh = kw_avg * model["cycle"]  # kWh per batch
    profile = model["steps"]["R101"]["batch"]["dosing"][0]["profile"]
    rates = [share * kwh / (seconds / 3600.0) for seconds, share in profile if share > 0]
    initiation, main = rates[0], rates[-1]
    e101 = next(e for e in _yaml("equipment/equipment-list.yaml")["equipment"] if e["tag"] == "E-101")
    notes = e101["notes"]
    assert "6.75 h" not in notes
    m = re.search(r"about (\d+) kW during the 5 h main dosing and (\d+) kW during the 15 min initiation", notes)
    assert m, notes
    assert abs(float(m.group(1)) - main) <= 0.05 * main, (m.group(1), main)
    assert abs(float(m.group(2)) - initiation) <= 0.05 * initiation, (m.group(2), initiation)
    assert re.search(rf"(\d+) kWh per batch", notes)
    assert abs(float(re.search(r"(\d+) kWh per batch", notes).group(1)) - kwh) <= 1.0, kwh


def test_toxic_methyl_bromide_release_is_stated_with_its_amount():
    d011 = _section("D-011")
    assert "toxic" in d011 and "never to atmosphere" in d011
    dosed = float(re.search(r"([\d.]+) kg \([\d.]+ kmol\) methyl bromide", _section("D-003")).group(1))
    acc = float(re.search(r"\| k/100 [^|]*\| ([\d.]+) % \|", d011).group(1)) / 100.0
    stated = float(re.search(r"about (\d+) kg at k/100", d011).group(1))
    assert abs(stated - acc * dosed) <= 0.05 * acc * dosed, (stated, acc * dosed)
    base = float(re.search(r"about (\d+) kg at the base rate", d011).group(1))
    acc_base = float(re.search(r"\| base \(ASSUMED k\) \| ([\d.]+) % \|", d011).group(1)) / 100.0
    assert abs(base - acc_base * dosed) <= 1.0, (base, acc_base * dosed)
    initiation = float(re.search(r"about (\d+) kg for an uninitiated 5 %", d011).group(1))
    assert abs(initiation - 0.998 * 0.05 * dosed) <= 1.0, (initiation, 0.05 * dosed)


def test_cake_quench_hydrogen_is_stated(model):
    x = _composition(model, "S8")
    comps = model["comps"]
    mm = sum(v * comps[c]["molar_mass"] for c, v in x.items())
    mg_kmol = _per_batch_kg(model, "S8") * x["MG"] / mm  # one H2 per Mg
    d007 = _section("D-007")
    assert "hydrogen" in d007 and "inerted" in d007
    kmol = float(re.search(r"about ([\d.]+) kmol, [\d.]+ kg or (\d+) Nm3 of hydrogen", d007).group(1))
    nm3 = float(re.search(r"about [\d.]+ kmol, [\d.]+ kg or (\d+) Nm3 of hydrogen", d007).group(1))
    assert abs(kmol - mg_kmol) <= 0.02, (kmol, mg_kmol)
    assert abs(nm3 - mg_kmol * NM3_PER_KMOL) <= 1.0, (nm3, mg_kmol * NM3_PER_KMOL)


#: J/(mol K), as core's thermochemistry
R_GAS = 8.314462618


def _mtt_at_vessel_pressure(model) -> float:
    """K: Clausius-Clapeyron from 2-MeTHF's normal boiling point and heat of vaporization at
    S3's pressure (core 1.9.0's default MTT, ADR 0058)."""
    methf = model["comps"]["METHF"]
    pressure = model["streams"]["S3"]["state"]["design"]["pressure"]["value"]
    tb, dh = methf["normal_boiling_point"], methf["heat_of_vaporization"]  # K, kJ/kmol = J/mol
    return 1.0 / (1.0 / tb - R_GAS * math.log(pressure / 101.325) / dh)


def _duty(model, sid: str) -> dict:
    return model["streams"][sid]["state"]["design"]["duty"]


def test_no_hand_set_mtt_and_the_default_is_stated(model):
    assert "mtt" not in model["steps"]["R101"]["hazard"], "core 1.9.0 takes the default MTT (D-011)"
    mtt = _mtt_at_vessel_pressure(model)
    assert abs(mtt - 356.33) < 0.05, mtt
    d011 = _section("D-011")
    assert f"MTT of {mtt:.1f} K" in d011 and f"MTT: core 1.9.0's default (ADR 0058), {mtt:.1f} K" in d011
    # thermo's 29.5 to 30.8 kJ/mol would give 356.9 to 357.1 K
    m = re.search(r"would give ([\d.]+) to ([\d.]+) K", d011)
    assert m, "D-011: the MTT from thermo's heats of vaporization"
    methf = dict(model["comps"]["METHF"])
    model_lo = {**model, "comps": {**model["comps"], "METHF": {**methf, "heat_of_vaporization": 30800}}}
    model_hi = {**model, "comps": {**model["comps"], "METHF": {**methf, "heat_of_vaporization": 29500}}}
    assert abs(float(m.group(1)) - _mtt_at_vessel_pressure(model_lo)) < 0.05
    assert abs(float(m.group(2)) - _mtt_at_vessel_pressure(model_hi)) < 0.05


def test_heating_medium_above_the_boiling_point_is_addressed(model):
    jacket = model["recipe"]["unit_procedures"][0]["vessel"]["jacket"]
    heating = jacket["heating_temperature"]
    tb = model["comps"]["METHF"]["normal_boiling_point"]  # the MTT once the pad is lost (D-010)
    mtt = _mtt_at_vessel_pressure(model)
    assert tb < heating < mtt, (tb, heating, mtt)
    d010 = _section("D-010")
    assert "above the solvent's normal boiling point" in d010 and "permissive for the dosing" in d010, (
        "the warm-up's medium lies above the normal boiling point: state it and its safeguard in D-010"
    )
    assert f"{mtt - heating:.1f} K below the MTT" in d010 and f"{mtt:.1f} K" in d010, d010


def test_r101_model_writes_q1_and_q2_stays_typed(model):
    r101 = model["steps"]["R101"]
    assert r101["energy_port"] == "q"
    q1 = model["streams"]["Q1"]
    assert q1["from"] == "R101.q"
    duty = _duty(model, "Q1")
    assert duty["provenance"] == "calculated" and duty.get("fingerprint"), duty
    assert abs(duty["value"] - 134.1) < 0.05, duty
    assert _duty(model, "Q2")["provenance"] == "assumed"
    with (PROCESS / "lca" / "inventory.csv").open(encoding="utf-8", newline="") as fh:
        rows = {r["key"]: r for r in csv.DictReader(fh)}
    brine, lps = rows["product:BRINE"], rows["feed:LPS"]
    assert brine["streams"].split() == ["Q1"] and brine["provenance"] == "calculated"
    assert abs(float(brine["plant"]) - duty["value"]) < 0.05, brine["plant"]
    assert "Q2" in lps["streams"].split(), lps["streams"]
    q2_q3 = _duty(model, "Q2")["value"] + _duty(model, "Q3")["value"]
    assert abs(float(lps["plant"]) - q2_q3) < 0.01, (lps["plant"], q2_q3)


def _d011_gas_column() -> dict[str, float]:
    """m3/h of the 'gas at the MTSR' column of D-011's sensitivity table, by case."""
    d011 = _section("D-011")
    gas = {}
    for name, key in (("base (ASSUMED k)", "base"), ("k/10", "k/10"),
                      ("k/100 (sluggish or delayed initiation)", "k/100"),
                      ("whole dose uninitiated (k/10000, dosing not stopped)", "whole")):
        m = re.search(rf"\| {re.escape(name)} \|(?:[^|]*\|){{3}} ([\d.]+) m3/h \|", d011)
        assert m, f"D-011: no gas release for {name}"
        gas[key] = float(m.group(1))
    return gas


def test_vent_capacity_against_the_gas_release(model):
    hazard = model["steps"]["R101"]["hazard"]
    capacity = hazard["vent_capacity"]
    assert capacity == 20.0 and hazard["provenance"] == "assumed"
    assert "ASSUMED" in hazard["source"] and "18.9 Nm3" in hazard["source"]
    gas = _d011_gas_column()
    assert gas["base"] < capacity and gas["k/10"] < capacity, gas
    assert gas["k/100"] > capacity and gas["whole"] > capacity, gas
    d011 = _section("D-011")
    assert "Design finding, the vent" in d011
    assert f"{gas['k/100'] / capacity:.1f} times the vent" in d011, gas["k/100"] / capacity


def test_screening_reproduces_the_stated_mtt_and_gas_release(model):
    """With core importable: the screening's own MTT and gas release are D-011's."""
    rh = pytest.importorskip("chemeascode.domains.safety.reaction_hazards")
    report = rh.screen(PROCESS)
    entry = next(e for e in report.entries if e.node == "R101")
    assert abs(entry.mtt - _mtt_at_vessel_pressure(model)) < 0.05, entry.mtt
    assert abs(entry.mtsr - 321.5) < 0.05, entry.mtsr
    assert "MEBR" in entry.mtt_left_out
    release = entry.gas_release
    assert release and release["vent_capacity_m3_h"] == 20.0
    assert abs(release["rate_m3_h"] - _d011_gas_column()["base"]) < 0.05, release["rate_m3_h"]
    assert release["capacity_ratio"] < 1.0


def test_published_with_cc_by():
    """Public by default (ADR 0036): the entry is published under CC-BY-4.0."""
    assert _yaml("process.yaml")["publication"] == {"status": "public", "license": "CC-BY-4.0"}
