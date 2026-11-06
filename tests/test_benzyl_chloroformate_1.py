"""benzyl-chloroformate-1 (#153): the folder's stated numbers against its own model.

Mostly fast, without core: the statements the folder makes in DESIGN.md, process.yaml and the
sources of its hand-written values are checked against the flowsheet's streams, materials and
reactions (review of process-library#384, and the moves to core 1.9.0 and 1.10.0):

- the LCI dataset and manifest record the hashes of the files they were written from, so an
  edit after ``cheme assess lca --write`` (which ``cheme assess lca --check`` rejects) fails here;
- the adiabatic rise core reports (494.0 K) is the side reaction CLBN's heat on the dissolved
  basis (391.4 K) plus the dose's heat of solution (102.6 K), as core takes the largest counted
  reaction run to completion and adds the heat of solution (ADR 0063); the main reaction PHOSG
  alone gives 220.8 K (323.4 K with the heat of solution), and those figures, with the MTSR of
  PHOSG alone (294.1 K), are stated where the screening is;
- the heats of PHOSG, CARB and CLBN are on the dissolved basis of phosgene (core ADR 0063: the
  dose's heat_of_solution, minus phosgene's heat of vaporization, is not counted twice), with 5 %
  of their HCl dissolved;
- Q2 is the semi-batch model's duty (R101 ``energy_port: q``, written by propagate, core ADR
  0059, 0063): the reactions' heat on their extents, the doses cooled and the absorbed phosgene's
  heat of solution; it holds the heat of absorption of what S5 keeps dissolved, which the still
  T101 takes back as Q4 and the removed hand stream Q2A (1.18 kW) used to carry; the brine per kg
  counts Q1 and Q2, and the recipe's jacket check takes the heat of solution;
- the vent capacity (hazard.vent_capacity) is the vacuum pump's suction volume, every reaction
  counts on purpose (hazard.reactions), and the gas release at the MTSR is above the capacity:
  a design finding stated in DESIGN.md D-014, checked against core's screening;
- the vacuum pump's volume for the degassing boil-up is the ideal gas at the still's pressure;
- R101's batch source names the dosing time the model uses (10 h, not the rejected 8 h);
- the REFERENCE.md process table stays sorted by id;
- the benzyl alcohol (feed:BNOH) links benzyl-alcohol-1's product the way feed:PHOS links
  phosgene-1: the linked dataset and product exist, the substance and unit are stream S1's, and
  the purity difference (S1 100 wt%, the product at least 99.8 wt%) is recorded as a proxy.
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


@pytest.fixture(scope="module")
def solution_rise(fs, comps):
    """K the dose's heat of solution adds to dT_ad (core ADR 0063): all the absorbed phosgene
    dissolving, over the same heat capacity."""
    r101 = _step(fs, "R101")
    dose = r101["batch"]["dosing"][0]
    moles = dict(_kmol(fs, comps, "S2"))
    for k, v in _kmol(fs, comps, dose["stream"]).items():
        moles[k] = moles.get(k, 0.0) + dose["absorbed"] * v
    capacity = sum(v * comps[k]["liquid_heat_capacity"] for k, v in moles.items() if v > 0)
    heats = dose["heat_of_solution"]["values"]
    return sum(-h * dose["absorbed"] * _kmol(fs, comps, dose["stream"])[k] for k, h in heats.items()) / capacity


def test_adiabatic_rise_is_the_side_reaction_clbn(adiabatic_rise, solution_rise):
    assert max(adiabatic_rise, key=adiabatic_rise.get) == "CLBN"
    assert round(adiabatic_rise["CLBN"], 1) == 391.4, adiabatic_rise
    assert round(adiabatic_rise["PHOSG"], 1) == 220.8, adiabatic_rise
    assert round(solution_rise, 1) == 102.6, solution_rise
    assert round(adiabatic_rise["CLBN"] + solution_rise, 1) == 494.0
    assert round(adiabatic_rise["PHOSG"] + solution_rise, 1) == 323.4


@pytest.mark.parametrize("rel", ["DESIGN.md", "process.yaml"])
def test_screening_names_the_reaction_behind_its_numbers(rel):
    text = _text(rel)
    for figure in ("220.8 K", "323.4 K", "294.1 K"):
        assert figure in text, f"{rel}: PHOSG alone ({figure}) is not stated next to the screening"
    if rel == "process.yaml":  # DESIGN.md D-015 records the 1.9.0 values it replaced
        for stale in ("474.6 K", "303.9 K", "300.2 K", "355.7 K", "3039 m3/h", "Q2A"):
            assert stale not in text, (rel, stale)
    assert "set by the phosgene accumulated" not in text, f"{rel}: the MTSR without CARB is CLBN's"


def test_screening_notes_and_description_state_phosg_alone():
    manifest = _yaml("process.yaml")
    assert "323.4 K" in manifest["description"] and "294.1 K" in manifest["description"]
    notes = manifest["validation"]["notes"]
    assert "323.4 K" in notes and "294.1 K" in notes and "494.0 K" in notes
    design = _text("DESIGN.md")
    l1 = design[design.index("- L-1:"):design.index("- L-2:")]
    assert "adiabatic rise" in l1 and "494.0 K" in l1 and "323.4 K" in l1, l1


# formation enthalpies of the liquids (kJ/kmol) as reactions.yaml's header cites them
_LIQUID_DHF = {"BCF": -376200.0, "BNOH": -160700.0, "BNCL": -32500.0}


def test_heats_of_reaction_are_on_the_dissolved_basis(fs, comps):
    """ADR 0063: with the dose's heat of solution the reactions consume dissolved phosgene, so
    each heat is the gas-basis one plus the heat of solution taken back per mol of phosgene, and
    5 % of the HCl formed stays dissolved (the vent's fraction) at minus its heat of
    vaporization: the absorption is counted once."""
    r101 = _step(fs, "R101")
    dose = r101["batch"]["dosing"][0]
    h_sol = dose["heat_of_solution"]["values"]
    assert set(h_sol) == {"COCL2"}
    assert h_sol["COCL2"] == -comps["COCL2"]["heat_of_vaporization"]  # ideal solution, ASSUMED
    assert dose["heat_of_solution"]["provenance"] == "assumed"
    retained = 1.0 - r101["batch"]["vent"]["fraction"]["HCL"]
    h_hcl = -comps["HCL"]["heat_of_vaporization"]
    reactions = {r["id"]: r for r in _yaml("process/reactions.yaml")["reactions"]}
    for rid in ("PHOSG", "CLBN"):
        nu = reactions[rid]["stoichiometry"]
        gas = sum(v * (_LIQUID_DHF.get(k) or comps[k]["ideal_gas"]["dHf_298"]) for k, v in nu.items())
        dissolved = gas + nu["COCL2"] * h_sol["COCL2"] + nu["HCL"] * retained * h_hcl
        assert reactions[rid]["heat_of_reaction"]["value"] == pytest.approx(dissolved, abs=1.0), rid
        assert "dissolved basis" in reactions[rid]["heat_of_reaction"]["source"]
    carb = reactions["CARB"]["heat_of_reaction"]["value"]
    assert carb == pytest.approx(-30000.0 + retained * h_hcl, abs=1.0)  # -30 kJ/mol ASSUMED


def _absorbed_kJ_h(fs, comps, sid) -> float:
    """Latent heat of the phosgene and HCl stream *sid* holds (kJ/h)."""
    n = _kmol(fs, comps, sid)
    return sum(n[k] * comps[k]["heat_of_vaporization"] for k in ("COCL2", "HCL"))


def test_q2_is_the_semibatch_model_duty(fs, comps):
    """Core writes R101's year-average duty on the stream at its energy_port: the heat its
    reactions release on their extents, the doses cooled to the batch (ADR 0059) and the
    absorbed phosgene's heat of solution (ADR 0063)."""
    r101 = _step(fs, "R101")
    assert r101["energy_port"] == "q"
    q2 = _stream(fs, "Q2")
    assert q2["from"] == "R101.q" and q2["to"].startswith("BRINE.")
    duty = q2["state"]["design"]["duty"]
    assert duty["provenance"] == "calculated" and "semibatch duty R101" in duty["source"]
    assert "fingerprint" in duty
    # extents from the outlets: BNCL is CLBN's, DBC is CARB's, BCF + DBC is PHOSG's
    out = {k: _kmol(fs, comps, "S5").get(k, 0.0) for k in ("BCF", "DBC", "BNCL")}
    extent = {"PHOSG": out["BCF"] + out["DBC"], "CARB": out["DBC"], "CLBN": out["BNCL"]}
    reactions = {r["id"]: r for r in _yaml("process/reactions.yaml")["reactions"]}
    heat = sum(-reactions[j]["heat_of_reaction"]["value"] * x for j, x in extent.items())  # kJ/h
    dose = r101["batch"]["dosing"][0]
    t4 = _stream(fs, "S4")["state"]["design"]["temperature"]["value"]
    t2 = _stream(fs, "S2")["state"]["design"]["temperature"]["value"]
    n4 = sum(_kmol(fs, comps, "S4").values())
    cooled = dose["absorbed"] * n4 * comps["COCL2"]["liquid_heat_capacity"] * (t4 - t2)
    solution = -dose["absorbed"] * n4 * dose["heat_of_solution"]["values"]["COCL2"]
    # the vented share's ideal-gas cooling (0.011 kW) is inside the tolerance
    assert duty["value"] * 3600.0 == pytest.approx(heat + cooled + solution, rel=0.002), (
        duty["value"], heat / 3600.0, cooled / 3600.0, solution / 3600.0,
    )
    assert duty["value"] == pytest.approx(19.884, abs=0.001)  # core 1.10.0


def test_q2_holds_the_absorption_heat_q4_takes_back(fs, comps):
    """The still charges the desorption of what stays dissolved to steam (Q4, its model's duty).
    On core 1.9.0 the semi-batch dissolved gas with no heat and the absorption of what S5 holds
    was the hand stream Q2A (1.18 kW); on 1.10.0 the dose's heat of solution with the reactions
    on the dissolved basis puts it in Q2: Q2 less its gas-basis value (core 1.9.0's 18.7043 kW) is
    that absorption, the latent heat S5 holds, to the 1.9.0 rounding (ADR 0063)."""
    q4 = _duty(fs, "Q4")
    assert q4["provenance"] == "calculated" and "still duty T101" in q4["source"]
    desorbed = _absorbed_kJ_h(fs, comps, "S7")
    assert desorbed == pytest.approx(q4["value"] * 3600.0, rel=0.01), (desorbed, q4)
    assert all(s["id"] != "Q2A" for s in fs["streams"])
    assert all(p["id"] != "q_abs" for p in _step(fs, "R101")["ports"])
    absorbed = _absorbed_kJ_h(fs, comps, "S5")
    assert absorbed >= desorbed
    gas_basis_q2 = 18.7043  # kW, core 1.9.0's model duty with the heats on the gas basis
    assert (_duty(fs, "Q2")["value"] - gas_basis_q2) * 3600.0 == pytest.approx(absorbed, rel=0.002)
    design = _text("DESIGN.md")
    assert f"Q2 {_duty(fs, 'Q2')['value']:.2f} kW" in design


def test_jacket_check_takes_the_heat_of_solution():
    """ADR 0063: the heat of solution is released at the dose's rate, so it is in the model's peak
    cooling duty and the recipe's jacket check (31.65 kW, 31.41 kW on 1.9.0 without it); the 10 h
    dosing still fits the jacket's 34.35 kW."""
    pytest.importorskip("chemeascode")
    from chemeascode.domains.process.recipe import recipe_report

    result = recipe_report(PROCESS)
    vessel = next(v for v in result.vessels if v.procedure == "PHOSGENATE")
    assert vessel.peak_duty == pytest.approx(31.65, abs=0.01)
    assert vessel.removable == pytest.approx(34.35, abs=0.01)
    assert vessel.peak_duty < vessel.removable
    design = _text("DESIGN.md")
    assert "the model's peak duty of 31.65 kW" in design
    notes = _yaml("equipment/equipment-list.yaml")["equipment"][0]["notes"]
    assert "peak duty 31.65 kW against 34.35 kW" in notes


def test_brine_per_kg_follows_q1_and_q2(fs):
    brine = sum(_duty(fs, q)["value"] for q in ("Q1", "Q2"))  # kW
    assert {s["id"] for s in fs["streams"] if s.get("to", "").startswith("BRINE.")} == {"Q1", "Q2"}
    product = _stream(fs, "S8")["state"]["design"]["flow"]["value"]  # kg/h
    per_kg = brine / product
    note = next(u["note"] for u in _yaml("process.yaml")["chemistry"]["utilities"]
                if u["inventory_key"] == "product:BRINE")
    m = re.match(r"([\d.]+) kWh/kg", note)
    assert m and float(m.group(1)) == pytest.approx(per_kg, abs=0.0006), (note, per_kg)
    d012 = re.search(r"brine ([\d.]+) kWh removed", _text("DESIGN.md"))
    assert d012 and float(d012.group(1)) == pytest.approx(per_kg, abs=0.0006), per_kg
    assert f"brine {brine:.2f} kW in all" in _text("DESIGN.md")
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


def _pump_volume(fs) -> float:
    """m3/h the vacuum pump draws at the still: the boil-up as an ideal gas at 20 kPa(a)."""
    still = _step(fs, "T101")["still"]
    t = _stream(fs, "S5")["state"]["design"]["temperature"]["value"]
    return still["boilup"]["value"] * R * t / still["pressure"]


def test_vent_capacity_is_the_vacuum_pump(fs):
    """D-014: the vent capacity is K-201's suction volume, the only path out of R-101, and every
    reaction counts on purpose (CARB kept, the conservative choice), each with its reason."""
    hazard = _step(fs, "R101")["hazard"]
    assert hazard["vent_capacity"] == pytest.approx(_pump_volume(fs), rel=0.02)
    assert hazard["vent_capacity"] == 173
    assert sorted(hazard["reactions"]) == sorted(_step(fs, "R101")["reactions"])
    assert hazard["provenance"] == "assumed"
    for word in ("vent_capacity", "K-201", "reactions", "CARB", "mtt", "no TD24"):
        assert word in hazard["source"], word
    assert "td24" not in hazard  # never estimated


def test_gas_release_above_the_vent_is_a_recorded_finding(fs):
    """The screening's gas release at the MTSR (3219 m3/h) is 18.6 times the vent: stated as a
    design finding with its measures, not silenced."""
    release = 0.01506 * R * 357.1 / 50.0 * 3600.0  # kmol/s at the MTSR and 50 kPa(a), m3/h
    assert release == pytest.approx(3219, rel=0.002)
    capacity = _step(fs, "R101")["hazard"]["vent_capacity"]
    assert round(3219 / capacity, 1) == 18.6
    design = _text("DESIGN.md")
    d014 = design[design.index("D-014 Gas release"):design.index("D-015 Core 1.10.0")]
    assert "3219 m3/h at 357.1 K and 50 kPa(a)" in d014 and "18.6 times the vent capacity" in d014
    for measure in ("dosing stops", "emergency relief", "never to air", "calorimetry"):
        assert measure in d014, measure
    # with CARB ruled out by calorimetry, PHOSG and CLBN still exceed the vent (D-011)
    assert "195 m3/h at 306.5 K, 1.13 times" in d014
    assert "about 195 m3/h by the screening, still 1.13 times" in d014
    assert "about 97 m3/h" not in d014
    notes = _yaml("process.yaml")["validation"]["notes"]
    assert "3219 m3/h" in notes and "18.6" in notes and "173 m3/h" in notes


def test_core_screens_the_gas_release_above_the_vent(fs):
    pytest.importorskip("chemeascode")
    from chemeascode.domains.safety.reaction_hazards import screen

    report = screen(PROCESS)
    entry = next(e for e in report.entries if e.node == "R101")
    assert entry.counted_reactions == ["PHOSG", "CARB", "CLBN"]
    assert entry.mtsr == pytest.approx(357.1, abs=0.05)
    assert entry.mtt == pytest.approx(280.65)
    assert entry.adiabatic_rise == pytest.approx(494.0, abs=0.05)
    assert entry.per_reaction["PHOSG"]["mtsr"] == pytest.approx(294.1, abs=0.05)
    assert entry.per_reaction["CLBN"]["mtsr"] == pytest.approx(306.5, abs=0.05)
    assert entry.per_reaction["PHOSG"]["adiabatic_rise"] == pytest.approx(220.8, abs=0.05)
    # ADR 0063: the heat of solution is in dT_ad, never in the MTSR
    solution = entry.heat_of_solution
    assert solution["adiabatic_rise_K"] == pytest.approx(102.6, abs=0.05)
    assert solution["in_mtsr"] is False
    gas = entry.gas_release
    assert gas["per_batch"] and gas["rate_m3_h"] == pytest.approx(3219, abs=0.5)
    assert gas["vent_capacity_m3_h"] == 173.0
    assert round(gas["capacity_ratio"], 1) == 18.6
    rules = {f.rule for f in report.findings if f.level in ("warning", "error")}
    # both are design findings recorded in DESIGN.md (D-011, D-014); nothing else may warn
    assert rules == {"cheme.reactor-hazard-mtsr", "cheme.reactor-hazard-vent"}, rules


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


def test_published_with_cc_by():
    """Public by default (ADR 0036): the entry is published under CC-BY-4.0."""
    assert _yaml("process.yaml")["publication"] == {"status": "public", "license": "CC-BY-4.0"}


def test_benzyl_alcohol_links_benzyl_alcohol_1(fs, comps):
    """feed:BNOH is linked to the library's benzyl-alcohol-1 (PR #402) as feed:PHOS is to phosgene-1."""
    mappings = _yaml("lca/mappings.yaml")["exchanges"]
    link, phos = mappings["feed:BNOH"]["dataset"], mappings["feed:PHOS"]["dataset"]
    assert set(link) == set(phos) == {"path", "product"}
    assert link["path"].startswith("processes/benzyl-alcohol-1/lca/")
    producer = yaml.safe_load((KIT / link["path"]).read_text(encoding="utf-8"))
    product = next(e for e in producer["exchanges"] if e["key"] == link["product"])
    assert product["type"] == "product"
    # same substance and unit as stream S1 and the consumer's exchange
    consumer = next(e for e in _yaml("lca/dataset.yaml")["exchanges"] if e["key"] == "feed:BNOH")
    assert product["unit"] == consumer["unit"] == "kg"
    assert producer["generation"]["formulas"][link["product"]] == comps["BNOH"]["formula"] == "C7H8O"
    feeds = {i["inventory_key"]: i["chemical"] for i in _yaml("process.yaml")["chemistry"]["inputs"]}
    made = {o["inventory_key"]: o["chemical"] for o in yaml.safe_load((KIT / "processes/benzyl-alcohol-1/process.yaml").read_text(encoding="utf-8"))["chemistry"]["outputs"]}
    assert feeds["feed:BNOH"] == made[link["product"]] == "benzyl-alcohol"
    # the purity difference is recorded as a proxy: S1 is pure in the model, the product 99.8 wt%
    assert _stream(fs, "S1")["state"]["design"]["composition"]["values"] == {"BNOH": 1.0}
    assert "at least 99.8 wt%" in product["title"]
    gap = 1.0 - 0.998
    assert f"{gap:.1%}" == "0.2%"
    design = _text("DESIGN.md")
    assert "Linked as a proxy for the dry alcohol: up to 0.2 % of the alcohol's burden is not counted" in design
    assert "up to 0.2 %" in mappings["feed:BNOH"]["source"]
    flow = next(f for f in _yaml("lca/lca.yaml")["flows"] if f["key"] == "feed:BNOH")
    assert flow["missing"].startswith("linked to processes/benzyl-alcohol-1 (lca/mappings.yaml)")
    assert "pending" not in flow["missing"] and "no library producer" not in _text("process.yaml")
