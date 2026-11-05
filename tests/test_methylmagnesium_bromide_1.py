"""methylmagnesium-bromide-1 (#157): the folder's stated numbers against its own files.

Fast, without core: the statements the folder makes in comments, in the equipment list and in
DESIGN.md are checked against the values its YAML files hold (review of process-library#383):

- the LCA dataset and manifest name the hashes of the input files as they are committed (the
  dataset went stale when process.yaml was edited after the last ``cheme assess lca --write``);
- the product's heat capacity in materials.yaml and DESIGN.md D-006 is what the declared liquid
  heat capacities and S9's composition give (1.58 kJ/(kg K), once stated as 1.66), and methyl
  bromide's 71.0 kJ/(kmol K) is thermo's value at 318 K, not at 298 K;
- E-101's duty during the dosing is the batch's vaporiser energy over the dosing segments that
  carry gas (once stated as 15 kW over a 6.75 h that no recipe interval has);
- D-011 names the toxic methyl bromide a cooling failure releases, in amounts that follow from
  the accumulation and the dose, and D-007 the hydrogen from quenching the magnesium cake;
- the warm-up's heating medium above the MTT is stated, with its safeguard, in D-010.
"""

from __future__ import annotations

import hashlib
import json
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


def test_heating_medium_above_the_mtt_is_addressed(model):
    jacket = model["recipe"]["unit_procedures"][0]["vessel"]["jacket"]
    mtt = model["steps"]["R101"]["hazard"]["mtt"]
    if jacket["heating_temperature"] <= mtt:
        return
    d010 = _section("D-010")
    assert "above the MTT" in d010 and "permissive for the dosing" in d010, (
        "the warm-up's medium lies above the MTT: state it and its safeguard in D-010"
    )
