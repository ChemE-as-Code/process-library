"""benzyl-chloroformate-1 (#153): the folder's stated numbers against its own model.

Fast, without core: the statements the folder makes in DESIGN.md, process.yaml and the sources of
its hand-written values are checked against the flowsheet's streams, materials and reactions
(review of process-library#384):

- the LCI dataset and manifest record the hashes of the files they were written from, so an
  edit after ``cheme assess lca --write`` (which ``cheme assess lca --check`` rejects) fails here;
- the adiabatic rise core reports (474.6 K) is the side reaction CLBN's heat, as core takes the
  largest single reaction run to completion; the main reaction PHOSG alone gives 303.9 K, and
  both figures, with the MTSR of PHOSG alone (300.1 K), are stated where the screening is;
- Q2 to brine includes the heat of absorption of the phosgene and HCl left dissolved in the crude
  S5, which the still T101 takes back as Q4 (core limit L-10), and the brine per kg follows;
- the vacuum pump's volume for the degassing boil-up is the ideal gas at the still's pressure;
- R101's batch source names the dosing time the model uses (10 h, not the rejected 8 h);
- the REFERENCE.md process table stays sorted by id.
"""

from __future__ import annotations

import hashlib
import json
import re
from itertools import pairwise
from pathlib import Path

import pytest
import yaml

KIT = Path(__file__).resolve().parents[1]
PROCESS = KIT / "processes" / "benzyl-chloroformate-1"
R = 8.314462618  # kJ/(kmol K)


def _yaml(rel: str):
    return yaml.safe_load((PROCESS / rel).read_text(encoding="utf-8"))


def _text(rel: str) -> str:
    return " ".join((PROCESS / rel).read_text(encoding="utf-8").replace("#", " ").split())


@pytest.fixture(scope="module")
def fs():
    return _yaml("process/flowsheet.yaml")


@pytest.fixture(scope="module")
def comps():
    return {c["id"]: c for c in _yaml("process/materials.yaml")["components"]}


def _stream(fs, sid):
    return next(s for s in fs["streams"] if s["id"] == sid)


def _step(fs, sid):
    return next(s for s in fs["steps"] if s["id"] == sid)


def _kmol(fs, comps, sid) -> dict[str, float]:
    """kmol/h of each component of stream *sid* (its design flow is in kg/h)."""
    d = _stream(fs, sid)["state"]["design"]
    x = d["composition"]["values"]
    if d["composition"]["basis"] == "mass_fraction":
        return {k: d["flow"]["value"] * v / comps[k]["molar_mass"] for k, v in x.items()}
    mw = sum(v * comps[k]["molar_mass"] for k, v in x.items())
    n = d["flow"]["value"] / mw
    return {k: n * v for k, v in x.items()}


def _duty(fs, sid) -> dict:
    return _stream(fs, sid)["state"]["design"]["duty"]


def _sha(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def test_lca_outputs_are_current_with_their_inputs():
    """cheme assess lca --check fails when an input changed after --write; so does this."""
    manifest = json.loads((PROCESS / "lca" / "manifest.json").read_text(encoding="utf-8"))
    dataset = _yaml("lca/dataset.yaml")
    recorded = {**manifest["inputs"], **dataset["provenance"]["files"]}
    assert "process.yaml" in recorded and "process/flowsheet.yaml" in recorded
    stale = [rel for rel, h in recorded.items() if _sha(PROCESS / rel) != h]
    assert not stale, f"edited after cheme assess lca --write: {stale}; rerun it and commit"


@pytest.fixture(scope="module")
def adiabatic_rise(fs, comps):
    """K per reaction of R101, as core's screening takes it: the reaction run to completion on
    the charge and the absorbed dose, over their liquid heat capacity."""
    r101 = _step(fs, "R101")
    dose = r101["batch"]["dosing"][0]
    moles = dict(_kmol(fs, comps, "S2"))
    for k, v in _kmol(fs, comps, dose["stream"]).items():
        moles[k] = moles.get(k, 0.0) + dose["absorbed"] * v
    capacity = sum(v * comps[k]["liquid_heat_capacity"] for k, v in moles.items() if v > 0)
    reactions = {r["id"]: r for r in _yaml("process/reactions.yaml")["reactions"]}
    out = {}
    for rid in r101["reactions"]:
        r = reactions[rid]
        extent = min(moles.get(n, 0.0) / -nu for n, nu in r["stoichiometry"].items() if nu < 0)
        out[rid] = -r["heat_of_reaction"]["value"] * extent / capacity
    return out


def test_adiabatic_rise_is_the_side_reaction_clbn(adiabatic_rise):
    assert max(adiabatic_rise, key=adiabatic_rise.get) == "CLBN"
    assert round(adiabatic_rise["CLBN"], 1) == 474.6, adiabatic_rise
    assert round(adiabatic_rise["PHOSG"], 1) == 303.9, adiabatic_rise


@pytest.mark.parametrize("rel", ["DESIGN.md", "process.yaml"])
def test_screening_names_the_reaction_behind_its_numbers(rel):
    text = _text(rel)
    for figure in ("303.9 K", "300.1 K"):
        assert figure in text, f"{rel}: PHOSG alone ({figure}) is not stated next to the screening"
    assert not re.search(r"whole neat batch,? 474\.6", text), f"{rel}: 474.6 K is CLBN's, not the batch's"
    assert "set by the phosgene accumulated" not in text, f"{rel}: the MTSR without CARB is CLBN's"


def test_screening_notes_and_description_state_phosg_alone():
    manifest = _yaml("process.yaml")
    assert "303.9 K" in manifest["description"] and "300.1 K" in manifest["description"]
    notes = manifest["validation"]["notes"]
    assert "303.9 K" in notes and "300.1 K" in notes
    design = _text("DESIGN.md")
    l1 = design[design.index("- L-1:"):design.index("- L-2:")]
    assert "adiabatic rise" in l1 and "474.6 K" in l1 and "303.9 K" in l1, l1


def test_q2_includes_the_absorption_heat_q4_takes_back(fs, comps):
    """The semi-batch dissolves gas with no heat (heats on the gas basis); the still charges the
    desorption of what stays dissolved to steam (Q4), so Q2 adds its absorption by hand."""
    s5 = _kmol(fs, comps, "S5")
    absorbed = sum(s5[k] * comps[k]["heat_of_vaporization"] for k in ("COCL2", "HCL"))  # kJ/h
    s7 = _kmol(fs, comps, "S7")
    desorbed = sum(s7[k] * comps[k]["heat_of_vaporization"] for k in ("COCL2", "HCL"))
    q4 = _duty(fs, "Q4")["value"] * 3600.0
    assert desorbed == pytest.approx(q4, rel=0.01), (desorbed, q4)
    assert absorbed >= desorbed
    q2 = _duty(fs, "Q2")
    m = re.search(r"released ([\d.]+) kJ per kmol of charge and doses", q2["source"])
    assert m, q2["source"]
    feed = sum(_kmol(fs, comps, "S1").values()) + sum(_kmol(fs, comps, "S4").values())
    released = float(m.group(1)) * feed
    assert q2["value"] * 3600.0 == pytest.approx(released + absorbed, rel=0.002), (
        q2["value"], released / 3600.0, absorbed / 3600.0,
    )


def test_brine_per_kg_follows_q1_and_q2(fs):
    brine = _duty(fs, "Q1")["value"] + _duty(fs, "Q2")["value"]  # kW
    product = _stream(fs, "S8")["state"]["design"]["flow"]["value"]  # kg/h
    per_kg = brine / product
    note = next(u["note"] for u in _yaml("process.yaml")["chemistry"]["utilities"]
                if u["inventory_key"] == "product:BRINE")
    m = re.match(r"([\d.]+) kWh/kg", note)
    assert m and float(m.group(1)) == pytest.approx(per_kg, abs=0.0006), (note, per_kg)
    d012 = re.search(r"brine ([\d.]+) kWh removed", _text("DESIGN.md"))
    assert d012 and float(d012.group(1)) == pytest.approx(per_kg, abs=0.0006), per_kg
    inventory = (PROCESS / "lca" / "inventory.csv").read_text(encoding="utf-8")
    row = next(r for r in inventory.splitlines() if r.startswith("product:BRINE,"))
    assert float(row.split(",")[5]) == pytest.approx(brine, rel=1e-4), row


@pytest.mark.parametrize(
    "rel", ["process/flowsheet.yaml", "DESIGN.md", "equipment/equipment-list.yaml"]
)
def test_vacuum_pump_volume_is_the_boilup_at_the_still(rel, fs):
    still = _step(fs, "T101")["still"]
    boilup = still["boilup"]
    assert boilup["unit"] == "kmol/h"
    t = _stream(fs, "S5")["state"]["design"]["temperature"]["value"]
    volume = boilup["value"] * R * t / still["pressure"]  # m3/h
    stated = re.findall(r"about (\d+) m3/h at 20 kPa\(a\) and 278 K", _text(rel))
    assert stated, f"{rel}: no vacuum-pump volume at 20 kPa(a) and 278 K"
    for v in stated:
        assert float(v) == pytest.approx(volume, rel=0.02), (rel, v, volume)


def test_r101_source_names_the_dosing_time(fs):
    r101 = _step(fs, "R101")
    hours = r101["batch"]["dosing"][0]["time"] / 3600.0
    m = re.search(r"dosed over ([\d.]+) h", r101["batch"]["source"])
    assert m and float(m.group(1)) == hours, (r101["batch"]["source"], hours)


def test_reference_process_table_sorted_by_id():
    table = (KIT / "REFERENCE.md").read_text(encoding="utf-8")
    ids = re.findall(r"^\| \[`([^`]+)`\]\(processes/", table, re.MULTILINE)
    assert "benzyl-chloroformate-1" in ids
    assert ids == sorted(ids), [(a, b) for a, b in pairwise(ids) if a > b]
