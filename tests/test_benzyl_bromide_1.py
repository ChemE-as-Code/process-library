"""benzyl-bromide-1 (#139): the folder's stated numbers against its own flowsheet.

Fast, without core: the flowsheet's streams (propagated by core and given by
scripts/balance.py) and the materials' data are read as YAML, and what the folder states in
DESIGN.md, process.yaml and lca/ is checked against them:

- the yields on the bromine and on the toluene make-up and the product's assay follow from the
  streams, and the assay carries its caveat (an upper bound) wherever it is stated;
- the absorber makes 48 wt% acid, and the allocation's shares are the mass of the product and of
  the HBr in the acid;
- the recycle S2 is 0.98 of the recovered toluene S17 at its fixed point, and the charge keeps 4
  mol of toluene per mol of bromine;
- every assumed temperature of a mixed stream is the adiabatic mix of its inlets, and the jacket
  is checked against the cooling water's mean temperature;
- every energy flow reaches the LCI: the cooling-water and brine totals per kg are the sums of
  their energy streams, the jacket duty Q2 counts the light and the agitator;
- the recipe's batch size times its batches gives 1000 t/a;
- the criticality classes DESIGN.md states as possible without a TD24 are those core's
  `criticality()` can give, and the MTT is below the content's bubble point at the worst moment;
  the k/100 bromine fraction is a share of the whole liquid at the end of the dosing;
- the lamp power's source states the 20 kW and the 5.25 h of light its duty uses; the residue
  left in C-101 is about 0.04 m3, inside the bottom head, and the jacket limit is recorded;
- the benzotribromide bound matches D-005's derivation, and every reaction source is a read
  entry of the source register;
- water ingress, the loss of the absorber water and the lamp wells (rupture, ignition in a
  flammable toluene atmosphere) are open items, and the process is not set public in the change
  that adds it (CONTRIBUTING, "Publishing a process");
- (core 1.9.0, ADR 0060) the toluene recycle S2 is a tear stream converged by propagate, not an
  assumed stream, at the splitter's 0.98;
- (core 1.9.0, ADR 0059) R101's model duty is on Q12 (the off-gas vapour's heat to the reflux
  condenser), the vapour's rest on Q13, and the jacket Q2 is the light and the agitator less Q13,
  so R-101's heat balance closes and the cooling water counts the vapour's heat once (in Q4);
  the stills' steam Q7 and Q9 are their models' latent heat, and the sensible heat core leaves
  out is the recorded exclusion of D-009, recomputed here from scripts/balance.py's still;
- (core 1.9.0, ADR 0058) R-101's off-gas capacity covers the HBr released at the MTSR, in the
  design case and in D-011's k/10 and k/100 cases, with the stated margin, and the vapour and the
  blocked vent stay open findings (D-014).
"""

from __future__ import annotations

import math
import re
from pathlib import Path

import pytest
import yaml

KIT = Path(__file__).resolve().parents[1]
PROCESS = KIT / "processes" / "benzyl-bromide-1"


def _yaml(rel: str) -> dict:
    return yaml.safe_load((PROCESS / rel).read_text(encoding="utf-8"))


def _text(rel: str) -> str:
    return " ".join((PROCESS / rel).read_text(encoding="utf-8").split())


@pytest.fixture(scope="module")
def model():
    materials = {c["id"]: c for c in _yaml("process/materials.yaml")["components"]}
    streams = {s["id"]: s for s in _yaml("process/flowsheet.yaml")["streams"]}
    return materials, streams


def _state(model, sid: str) -> dict:
    return model[1][sid]["state"]["design"]


def _kmol(model, sid: str) -> dict[str, float]:
    """kmol/h of each component of a material stream."""
    materials, _ = model
    state = _state(model, sid)
    flow, comp = state["flow"]["value"], state["composition"]
    if comp["basis"] == "mole_fraction":
        mm = sum(x * materials[k]["molar_mass"] for k, x in comp["values"].items())
        return {k: flow / mm * x for k, x in comp["values"].items()}
    return {k: flow * w / materials[k]["molar_mass"] for k, w in comp["values"].items()}


def _kg(model, sid: str) -> dict[str, float]:
    return {k: n * model[0][k]["molar_mass"] for k, n in _kmol(model, sid).items()}


def _mcp(model, sid: str) -> float:
    return sum(n * model[0][k]["liquid_heat_capacity"] for k, n in _kmol(model, sid).items() if n)


def _temperature(model, sid: str) -> float:
    return _state(model, sid)["temperature"]["value"]


def _duty(model, sid: str) -> float:
    return _state(model, sid)["duty"]["value"]


def test_yields_and_assay_follow_from_the_flowsheet(model):
    product = _kmol(model, "S15")["BNBR"]
    assert product / _kmol(model, "S5")["BR2"] == pytest.approx(0.8846, abs=5e-4)
    assert product / _kmol(model, "S1")["TOL"] == pytest.approx(0.869, abs=5e-4)
    masses = _kg(model, "S15")
    assert masses["BNBR"] / sum(masses.values()) == pytest.approx(0.983, abs=5e-4)
    for rel in ("DESIGN.md", "process.yaml"):
        text = _text(rel)
        assert "88.5 %" in text and "86.9 %" in text and "98.3 wt%" in text, rel
    rate = _state(model, "S15")["flow"]["value"]
    assert _state(model, "S5")["flow"]["value"] / rate == pytest.approx(1.038, abs=5e-4)
    assert _state(model, "S1")["flow"]["value"] / rate == pytest.approx(0.609, abs=5e-4)


def test_the_assay_and_the_yield_carry_their_caveats():
    """The assay is an upper bound (by-products not modelled) everywhere it is stated, and the
    modelled yield on toluene is said to stay below the source's 90 %."""
    manifest = _yaml("process.yaml")
    assert "upper bound" in " ".join(manifest["description"].split())
    note = next(o for o in manifest["chemistry"]["outputs"] if o["inventory_key"] == "product:BNBR")
    assert "upper bound" in note["note"]
    assert "upper bound" in _yaml("process/design-basis.yaml")["products"][0]["purity"]
    assert "upper bound" in _text("README.md")
    design = _text("DESIGN.md")
    assert "The 98.3 wt% is an upper bound" in design
    assert "The modelled yield on toluene is below the source's" in design
    assert 0.869 < 0.90  # SRC-1, Example I: about 90 % on toluene


def test_acid_strength_and_the_allocation_shares(model):
    acid = _kg(model, "S11")
    assert acid["HBR"] / sum(acid.values()) == pytest.approx(0.48, abs=1e-3)
    product = _state(model, "S15")["flow"]["value"]
    allocation = _yaml("lca/lca.yaml")["allocation"]
    share = product / (product + acid["HBR"])
    assert allocation["shares"]["BNBR"] == pytest.approx(share, abs=1e-4)
    assert allocation["shares"]["HBRACID"] == pytest.approx(1 - share, abs=1e-4)
    assert sum(allocation["shares"].values()) == pytest.approx(1.0)


def test_recycle_at_its_fixed_point_and_the_charge_ratio(model):
    # core 1.9.0 (ADR 0060): S2 is the tear stream, converged and written by propagate
    sheet = _yaml("process/flowsheet.yaml")
    assert [t["stream"] for t in sheet["tears"]] == ["S2"]
    splitter = next(s for s in sheet["steps"] if s["id"] == "SP201")
    assert splitter["split"] == {"rec": 0.98}
    for key in ("flow", "composition"):
        value = _state(model, "S2")[key]
        assert value["provenance"] == "calculated" and "(tear, wegstein)" in value["source"], key
    s2, s17 = _kmol(model, "S2"), _kmol(model, "S17")
    for k, n in s17.items():
        assert s2.get(k, 0.0) == pytest.approx(0.98 * n, rel=2e-3, abs=1e-6), k
    charge = _kmol(model, "S4")
    assert charge["TOL"] / _kmol(model, "S5")["BR2"] == pytest.approx(4.0, rel=2e-3)


def _mix(model, *parts: tuple[str, float]) -> float:
    return sum(_mcp(model, s) * t for s, t in parts) / sum(_mcp(model, s) for s, _ in parts)


def test_mixed_temperatures_are_the_adiabatic_mixes(model):
    t3 = _mix(model, ("S1", _temperature(model, "S1")), ("S2", _temperature(model, "S2")))
    assert _temperature(model, "S3") == pytest.approx(t3, abs=0.05)
    t17 = _mix(model, ("S12", _temperature(model, "S12")), ("S14", _temperature(model, "S14")))
    assert _temperature(model, "S17") == pytest.approx(t17, abs=0.05)
    for sid in ("S2", "S18"):
        assert _temperature(model, sid) == pytest.approx(t17, abs=0.05), sid
    recipe = _yaml("process/recipe.yaml")
    heat = next(o for o in recipe["unit_procedures"][0]["operations"] if o["id"] == "heat")
    assert heat["temperatures"][0] == pytest.approx(t3, abs=0.05)


def test_jackets_against_the_mean_coolant_and_the_brine_above_bromine_freezing(model):
    products = {p["id"]: p for p in _yaml("process/flowsheet.yaml")["products"]}
    cw = products["CW"]["utility"]
    mean = 0.5 * (cw["supply_temperature"]["value"] + cw["return_temperature"]["value"])
    jacket = _yaml("process/recipe.yaml")["unit_procedures"][0]["vessel"]["jacket"]
    assert jacket["coolant_temperature"] == pytest.approx(mean)
    # the vent gas and the forerun leave the brine coolers above bromine's 265.95 K melting point
    for sid in ("S9", "S14"):
        assert _temperature(model, sid) > 265.95 + 2.0, sid


def test_every_energy_flow_reaches_the_lci(model):
    _, streams = model
    energy = [s for s in streams.values() if s.get("kind") == "energy"]
    rate = _state(model, "S15")["flow"]["value"]
    by_sink = {}
    for s in energy:
        by_sink.setdefault(s["to"].split(".")[0], []).append(s["id"])
        by_sink.setdefault(s["from"].split(".")[0], []).append(s["id"])
    assert set(by_sink["CW"]) == {"Q2", "Q3", "Q4", "Q6", "Q8", "Q11"}
    assert set(by_sink["BRINE"]) == {"Q5", "Q10"}
    assert set(by_sink["LPS"]) == {"Q1", "Q7", "Q9"}
    assert set(by_sink["POWER"]) == {"P1", "P2", "P3"}
    per_kg = {k: sum(_duty(model, q) for q in v) / rate for k, v in by_sink.items() if k in ("CW", "BRINE", "LPS", "POWER")}
    assert per_kg["CW"] == pytest.approx(0.634, abs=5e-4)
    assert per_kg["BRINE"] == pytest.approx(0.044, abs=5e-4)
    assert per_kg["LPS"] == pytest.approx(0.392, abs=5e-4)
    assert per_kg["POWER"] == pytest.approx(0.156, abs=5e-4)
    design, manifest = _text("DESIGN.md"), _text("process.yaml")
    for figure in ("0.634 kWh", "0.044 kWh", "0.392 kWh", "0.156 kWh"):
        assert figure in design and figure in manifest, figure
    inventory = {row.split(",")[0]: row for row in (PROCESS / "lca" / "inventory.csv").read_text(encoding="utf-8").splitlines()[1:]}
    assert {"product:CW", "product:BRINE", "feed:LPS", "feed:POWER"} <= set(inventory)
    # Q2 counts the light the content absorbs (30 % of the lamps' power) and the 3 kW agitator
    assert "agitator" in streams["Q2"]["state"]["design"]["duty"]["source"]
    assert _duty(model, "Q3") == pytest.approx(0.7 * _duty(model, "P1"), rel=1e-3)
    assert "Recorded exclusions, each with its number" in design


def test_recipe_basis_gives_1000_t_per_year(model):
    recipe = _yaml("process/recipe.yaml")
    rate = _state(model, "S15")["flow"]["value"]
    hours = recipe["hours_per_year"]["value"]
    assert rate * hours / 1000 == pytest.approx(1000, rel=1e-3)
    batches = rate * hours / recipe["batch_size"]["value"]
    assert batches == pytest.approx(1124.1, abs=0.2)  # D-003


def _criticality(mtsr: float, mtt: float, td24: float) -> int:
    """Stoessel's class as core v1.8.0's reaction_hazards.criticality gives it."""
    if td24 < mtsr:
        return 4 if mtt < td24 else 5
    if mtsr < mtt:
        return 1 if mtt < td24 else 2
    return 3


def test_the_stated_criticality_classes_are_those_any_td24_can_give():
    rows = re.findall(
        r"^\| (?:5\.0e-4 \(design\)|k/10|k/100) \| [^|]+ \| ([\d.]+) K \| [^|]+ \| [^|]+ \| [^|]+ \| [^|]+ \| ([^|]+) \|$",
        (PROCESS / "DESIGN.md").read_text(encoding="utf-8"),
        flags=re.M,
    )
    assert len(rows) == 3
    mtt = 383.8
    for mtsr, stated in rows:
        possible = {_criticality(float(mtsr), mtt, 300.0 + 0.5 * i) for i in range(600)}
        assert {int(c) for c in re.findall(r"\d", stated)} == possible, (mtsr, stated)
    assert "and 5 if it lies below (TD24 < 363.9 K" in _text("DESIGN.md")


def _bubble(materials: dict, x: dict[str, float], p: float = 101.325) -> float:
    def total(t: float) -> float:
        out = 0.0
        for k, xi in x.items():
            vp = materials[k]["vapour_pressure"]
            out += xi * 100.0 * 10 ** (vp["a"] - vp["b"] / (t + vp["c"]))
        return out

    lo, hi = 250.0, 600.0
    for _ in range(100):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if total(mid) < p else (lo, mid)
    return mid


def test_the_mtt_is_below_the_content_bubble_point_in_the_design_case(model):
    materials, _ = model
    hazard = next(s for s in _yaml("process/flowsheet.yaml")["steps"] if s["id"] == "R101")["hazard"]
    end = {k: v for k, v in _state(model, "S6")["composition"]["values"].items() if v and k != "HBR"}
    # the worst moment: the end of the dosing with 1.73 % of the 5.777 kmol of bromine unreacted
    x_br2 = 0.0173 * 5.777 / 25.088
    worst = {k: v * (1 - x_br2) for k, v in end.items()}
    worst["BR2"] = x_br2
    assert _bubble(materials, worst) == pytest.approx(394.9, abs=0.3)
    assert hazard["mtt"] < _bubble(materials, worst)
    assert "394.9 K at the worst moment" in _text("DESIGN.md")


def _per_batch(model, sid: str) -> dict[str, float]:
    cycle = _yaml("process/recipe.yaml")["hours_per_year"]["value"] / 1124.1
    return {k: n * cycle for k, n in _kmol(model, sid).items() if k != "HBR"}


def test_the_k100_bromine_fraction_counts_the_liquid_at_the_end_of_dosing(model):
    """At k/100 (accumulation 73.1 %) the bromine left is a share of the whole liquid: the
    charge plus the bromine dosed less one mole per mole reacted (the HBr is vented), not of
    the charge alone."""
    materials, _ = model
    charge, dosed = _per_batch(model, "S4"), _per_batch(model, "S5")["BR2"]
    reacted = (1 - 0.731) * dosed
    liquid = dict(charge)
    liquid["BR2"] = liquid.get("BR2", 0.0) + dosed - reacted
    liquid["TOL"] -= reacted
    liquid["BNBR"] += reacted
    total = sum(liquid.values())
    assert total == pytest.approx(29.31, abs=0.02)
    assert liquid["BR2"] / total == pytest.approx(0.144, abs=1e-3)
    bubble = _bubble(materials, {k: v / total for k, v in liquid.items() if v > 0})
    assert bubble == pytest.approx(372.3, abs=0.5)
    design = _text("DESIGN.md")
    assert "about 14 mol% bromine at the end of the dosing (4.2 kmol in 29.3 kmol of liquid" in design
    assert "17 mol% bromine" not in design
    assert "about 372 K at k/100" in design and "about 373 K" not in design


def test_the_lamp_power_source_states_the_lamps_and_hours_the_duty_uses(model):
    """P1 is 20 kW over the 5.25 h of light a batch (dosing and post-reaction), as a year
    average; the source names those, not a rating over the dosing alone."""
    recipe = _yaml("process/recipe.yaml")
    light_h = 18_891.8 / 3600.0  # scripts/balance.py LIGHT_S
    p1 = 20.0 * light_h * 1124.1 / recipe["hours_per_year"]["value"]
    assert _duty(model, "P1") == pytest.approx(p1, rel=1e-3)
    source = _state(model, "P1")["duty"]["source"]
    assert "20 kW of lamps" in source and "5.25 h of light" in source
    assert "30 kW" not in _text("process/flowsheet.yaml")
    balance = (PROCESS / "scripts" / "balance.py").read_text(encoding="utf-8")
    assert "P_LAMP = 20.0" in balance and "LIGHT_S = 18_891.8" in balance


def test_the_residue_left_in_c101_and_its_jacket(model):
    """The residue at the end of ST102 is about 0.04 m3, inside C-101's dished bottom, and the
    note and D-007 say the end of the main cut cannot run at the stated boil-up."""
    materials, _ = model
    residue = _per_batch(model, "S16")
    volume = sum(n * materials[k]["liquid_molar_volume"] for k, n in residue.items())
    mass = sum(n * materials[k]["molar_mass"] for k, n in residue.items())
    assert mass == pytest.approx(68.7, abs=0.1)
    assert volume == pytest.approx(0.0426, abs=1e-3)
    assert volume < 0.0998 * 1.62**3  # the DIN 28011 bottom of C-101
    note = _text("equipment/equipment-list.yaml")
    assert "about 0.04 m3 (68.7 kg) is left at the end of ST102, inside the bottom head" in note
    assert "0.3 m3 left" not in note
    assert "cannot run at the stated 80 kW" in note
    design = _text("DESIGN.md")
    assert "The end of the main cut cannot run at 80 kW." in design
    assert "C-101 is then busy 4.78 h of the 7.05 h cycle" in design


def test_the_lamp_wells_and_flammability_are_open_items():
    design = _text("DESIGN.md")
    assert "(d) The lamp wells and flammability." in design
    for item in ("toluene's flash point of 4 C", "lower explosive limit of 1.1 vol%",
                 "a path apart from the jacket leak of (b)", "O2 check", "air in-leakage into the vacuum stills"):
        assert item in design, item
    equipment = _text("equipment/equipment-list.yaml")
    assert "lamp power tripped on a well-coolant fault" in equipment
    assert "D-011 (d)" in equipment


def test_benzotribromide_bound_matches_its_derivation():
    """reactions.yaml states the bound D-005 derives: 0.037 x the 4.5 % of the bromine BALBR
    takes, below 0.2 % of the bromine."""
    header = (PROCESS / "process" / "reactions.yaml").read_text(encoding="utf-8")
    assert "below 0.2 % of the\n# bromine" in header
    assert "0.1 % of the" not in header
    assert 0.037 * 0.045 < 0.002
    assert "below 0.2 % of the bromine (0.037 x the 4.5 % that BALBR takes)" in _text("DESIGN.md")


def test_every_reaction_source_is_a_read_source_of_the_register():
    """Each `sources:` entry of reactions.yaml names a register entry that was read."""
    register = {}
    for line in (PROCESS / "DESIGN.md").read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\| (SRC-\d+) \|(?:[^|]*\|){2} ([^|]*) \|", line)
        if m:
            register[m.group(1)] = m.group(2)
    for reaction in _yaml("process/reactions.yaml")["reactions"]:
        for entry in reaction["sources"]:
            cited = re.findall(r"SRC-\d+", entry)
            assert cited, (reaction["id"], entry)
            for src in cited:
                assert register[src].startswith("read"), (reaction["id"], src)
            assert "snippet" not in entry and "not used" not in entry, (reaction["id"], entry)


def test_water_ingress_and_absorber_water_loss_are_open_items():
    design = _text("DESIGN.md")
    assert "Loss of the absorber water while R-101 doses" in design
    assert "Water ingress into R-101" in design
    equipment = _text("equipment/equipment-list.yaml")
    assert "suck-back" in equipment and "A-101's water flow" in equipment
    assert "caustic guard scrubber" in equipment


def test_not_published_in_the_change_that_adds_it():
    publication = _yaml("process.yaml")["publication"]
    assert publication["status"] == "internal"
    assert "license" not in publication


# core 1.9.0 (ADRs 0058 to 0060)

T_REACT, T_SUPPLY, T_CW, T_VENT, P_ATM = 363.15, 298.15, 303.15, 268.15, 101.325


def _p_sat(materials: dict, k: str, t: float) -> float:
    vp = materials[k]["vapour_pressure"]
    return 100.0 * 10 ** (vp["a"] - vp["b"] / (t + vp["c"]))


def _carried(model, sid: str) -> float:
    """mol of the liquid's vapour per mol of HBr leaving at 363.15 K (Raoult, D-008)."""
    materials, _ = model
    liquid = {k: n for k, n in _kmol(model, sid).items() if n > 0 and k != "HBR"}
    total = sum(liquid.values())
    p = sum(n / total * _p_sat(materials, k, T_REACT) for k, n in liquid.items())
    return p / (P_ATM - p)


def _energy(model) -> dict[str, dict]:
    return {k: s for k, s in model[1].items() if s.get("kind") == "energy"}


def test_r101_model_duty_on_q12_and_its_heat_balance(model):
    materials, _ = model
    energy = _energy(model)
    q12 = energy["Q12"]["state"]["design"]["duty"]
    assert q12["provenance"] == "calculated" and "semibatch duty R101" in q12["source"]
    r101 = next(s for s in _yaml("process/flowsheet.yaml")["steps"] if s["id"] == "R101")
    assert r101["energy_port"] == "reflux"
    assert energy["Q12"]["from"] == "R101.reflux" and energy["Q12"]["to"] == "E102.reflux"
    # the model: one HBr per extent of BNBR and BALBR, both -32.3 kJ/mol, less the bromine warmed
    reactions = 32_300.0 * _kmol(model, "S7")["HBR"]
    warm = _kmol(model, "S5")["BR2"] * materials["BR2"]["liquid_heat_capacity"] * (T_REACT - T_SUPPLY)
    assert q12["value"] == pytest.approx((reactions - warm) / 3600.0, rel=1e-4)
    # the vapour the HBr carries (D-008): its latent heat and the reheating of what returns
    n_hbr = _kmol(model, "S7")["HBR"]
    r_out = 0.5 * (_carried(model, "S4") + _carried(model, "S6"))
    r_cw = _p_sat(materials, "TOL", T_CW) / (P_ATM - _p_sat(materials, "TOL", T_CW))
    r_vent = _p_sat(materials, "TOL", T_VENT) / (P_ATM - _p_sat(materials, "TOL", T_VENT))
    lam, cp = materials["TOL"]["heat_of_vaporization"], materials["TOL"]["liquid_heat_capacity"]
    vapour = n_hbr * (r_out * lam + (r_out - r_cw) * cp * (T_REACT - T_CW) + (r_cw - r_vent) * cp * (T_REACT - T_VENT)) / 3600.0
    assert vapour == pytest.approx(8.244, abs=2e-3)
    assert _duty(model, "Q13") == pytest.approx(vapour - q12["value"], abs=2e-4)
    assert _duty(model, "Q13") > 0  # the vapour takes more than the model's duty
    light = 0.3 * _duty(model, "P1")
    assert _duty(model, "Q2") == pytest.approx(light + _duty(model, "P2") - _duty(model, "Q13"), abs=2e-4)
    # the lamps: their electricity P1 is the light the content absorbs plus the wells' Q3
    assert _duty(model, "P1") == pytest.approx(light + _duty(model, "Q3"), abs=2e-4)
    # R-101's full balance without Q12 and Q13: in the reactions (less the warming), the light and
    # the agitator; out the jacket Q2 and the vapour's heat, both computed here
    assert (reactions - warm) / 3600.0 + light + _duty(model, "P2") == pytest.approx(_duty(model, "Q2") + vapour, abs=5e-4)
    # on the jacket the model would differ by a net that flows against it (D-009)
    assert light + _duty(model, "P2") - vapour == pytest.approx(-0.77, abs=0.01)
    design = _text("DESIGN.md")
    assert "+4.47 + 3.0 - 8.24 = -0.77 kW" in design
    assert "`energy_port: reflux`" in design


def test_q12_and_q13_reach_the_lci_once_through_the_reflux_condenser(model):
    energy = _energy(model)
    for q in ("Q12", "Q13"):
        assert energy[q]["to"].startswith("E102."), q
    inventory = (PROCESS / "lca" / "inventory.csv").read_text(encoding="utf-8")
    cw = next(line for line in inventory.splitlines() if line.startswith("product:CW,"))
    assert cw.endswith(",Q2 Q3 Q4 Q6 Q8 Q11")
    assert "Q12" not in inventory and "Q13" not in inventory


def test_the_stills_steam_is_the_model_and_the_sensible_heat_is_recorded(model):
    materials, _ = model
    energy = _energy(model)
    for q, node, cuts in (("Q7", "ST101", ("S12",)), ("Q9", "ST102", ("S14", "S15"))):
        duty = energy[q]["state"]["design"]["duty"]
        assert duty["provenance"] == "calculated" and f"still duty {node}" in duty["source"], q
        latent = sum(n * materials[k]["heat_of_vaporization"] for s in cuts for k, n in _kmol(model, s).items() if n)
        assert duty["value"] == pytest.approx(latent / 3600.0, rel=2e-4), q
    steps = {s["id"]: s for s in _yaml("process/flowsheet.yaml")["steps"]}
    assert steps["ST101"]["energy_port"] == "steam" and steps["ST102"]["energy_port"] == "steam"
    design = _text("DESIGN.md")
    assert "2.41 kW (0.019 kWh/kg) less LP steam" in design
    assert "**The hand values were too low**" in design
    assert "23.23 kW for ST101 (sensible -1.33) and 12.55 for ST102 (-1.08)" in design
    # "4.9 % high" of the LCI's steam: the model's Q7 and Q9 with the heat-up Q1, as feed:LPS
    lps = sum(_duty(model, q) for q in ("Q1", "Q7", "Q9"))
    inventory = (PROCESS / "lca" / "inventory.csv").read_text(encoding="utf-8").splitlines()
    row = next(line for line in inventory if line.startswith("feed:LPS,"))
    assert row.endswith(",Q1 Q7 Q9")
    assert float(row.split(",kWh/h,")[0].rsplit(",", 1)[1]) == pytest.approx(lps, abs=1e-3)
    assert 2.41 / lps == pytest.approx(0.049, abs=5e-4)


def test_the_stills_full_balance_from_the_script(model):
    """scripts/balance.py's repeat of the stills gives core's cuts and the stated sensible heat."""
    import importlib.util

    spec = importlib.util.spec_from_file_location("bnbr_balance", PROCESS / "scripts" / "balance.py")
    balance = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(balance)
    materials, _ = model
    s6, s13 = _kmol(model, "S6"), _kmol(model, "S13")
    strip = balance.rayleigh(materials, s6, 15.0, [("top", lambda x: x.get("TOL", 0.0) <= 0.15)])
    vac = balance.rayleigh(
        materials, s13, 2.0,
        [("fore", lambda x: x.get("TOL", 0.0) <= 0.002), ("main", lambda x: x.get("BNBR", 0.0) <= 0.35)],
    )
    for cut, sid in ((strip["top"], "S12"), (vac["fore"], "S14"), (vac["main"], "S15")):
        assert sum(cut["moles"].values()) == pytest.approx(sum(_kmol(model, sid).values()), rel=2e-3), sid
    sens7 = balance.sensible(materials, strip, T_REACT) / 3600.0
    sens9 = balance.sensible(materials, vac, _temperature(model, "S13")) / 3600.0
    assert sens7 == pytest.approx(-1.33, abs=0.01) and sens9 == pytest.approx(-1.08, abs=0.01)
    assert -(sens7 + sens9) == pytest.approx(2.41, abs=0.01)
    assert balance.condenser(materials, strip["top"], T_CW) / 3600.0 == pytest.approx(_duty(model, "Q8"), rel=2e-3)
    assert balance.condenser(materials, vac["fore"], T_VENT) / 3600.0 == pytest.approx(_duty(model, "Q10"), rel=2e-3)


def test_the_off_gas_capacity_covers_the_gas_release_at_the_mtsr():
    r101 = next(s for s in _yaml("process/flowsheet.yaml")["steps"] if s["id"] == "R101")
    hazard = r101["hazard"]
    capacity = hazard["vent_capacity"]
    assert hazard["provenance"] == "assumed" and "1.2 x the largest gas release" in hazard["source"]

    def m3_h(mol_s: float, t: float) -> float:
        return mol_s * 1e-3 * 8.314 * t / P_ATM * 3600.0

    release = m3_h(0.3265, 363.93)
    assert release == pytest.approx(35.10, abs=0.03)
    assert capacity == 5.0 * math.ceil(1.2 * release / 5.0) == 45.0
    assert 34.32 < capacity  # the normal peak (cheme process recipe)
    table = (PROCESS / "DESIGN.md").read_text(encoding="utf-8").splitlines()
    for name, (rate, mtsr, stated) in {
        "5.0e-4 (design)": (0.3265, 363.93, 35.10),
        "k/10": (0.3758, 370.47, 41.13),
        "k/100": (0.3276, 394.57, 38.18),
    }.items():
        assert m3_h(rate, mtsr) == pytest.approx(stated, rel=2e-3), name
        row = next(line for line in table if line.startswith(f"| {name} |"))
        assert f"{stated:.2f} m3/h: {stated / capacity:.2f} x" in row, name
        assert stated < capacity, name
    design = _text("DESIGN.md")
    assert "`hazard.vent_capacity: 45`" in design
    # the blocked vent: the accumulated bromine's HBr in R-101's 1.02 m3 head space
    head = 4.0 - 2.982
    assert 0.0999 * 8.314 * 363.93 / head / 1000.0 == pytest.approx(0.30, abs=0.005)
    assert 0.946 * 8.314 * 370.47 / head / 1000.0 == pytest.approx(2.86, abs=0.02)
    assert "by about 0.30 MPa at 363.9 K" in design and "by about 2.9 MPa at 370.5 K" in design
    assert "So R-101 needs a relief device" in design
    # the vapour with the gas at the k/10 MTSR and the line it needs
    ratio = float(re.search(r"and ([0-9.]+) at the k/10 MTSR", design).group(1))
    assert ratio == pytest.approx(1.51)
    assert capacity * (1.0 + ratio) == pytest.approx(115, abs=3)
    assert "about 115 m3/h" in design


def test_core_screens_the_gas_release_within_the_off_gas_capacity():
    pytest.importorskip("chemeascode")
    from chemeascode.domains.safety.reaction_hazards import screen

    report = screen(PROCESS)
    (entry,) = report.entries
    gas = entry.gas_release
    assert gas["per_batch"] and gas["rate_m3_h"] == pytest.approx(35.10, abs=0.05)
    assert gas["vent_capacity_m3_h"] == 45.0 and gas["capacity_ratio"] < 1.0
    assert entry.mtsr == pytest.approx(363.9, abs=0.05)
    assert not [f for f in report.findings if f.level in ("warning", "error")]


def test_requires_core_1_9():
    plant = _yaml("plant.yaml")
    assert plant["requires"] == "cheme-as-code>=1.9"
    for rel in ("README.md", "process.yaml"):
        assert "Needs cheme-as-code 1.9.0" in _text(rel), rel
