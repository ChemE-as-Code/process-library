"""benzyl-bromide-1 (#139): the folder's stated numbers against its own flowsheet.

Fast, without core: the flowsheet's streams (propagated by core and given by
scripts/balance.py) and the materials' data are read as YAML, and what the folder states in
DESIGN.md, process.yaml and lca/ is checked against them:

- the yields on the bromine and on the toluene make-up and the product's assay follow from the
  streams, and the assay carries its caveat (an upper bound) wherever it is stated;
- the absorber makes 48 wt% acid on HBr and water, and the allocation's shares are the mass of
  the product and of the HBr in the acid;
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
- the lamp power's source states the 20 kW and the 5.24 h of light its duty uses; the residue
  left in C-101 is about 0.04 m3, inside the bottom head, and the jacket limit is recorded;
- the benzotribromide bound matches D-005's derivation, and every reaction source is a read
  entry of the source register;
- water ingress, the loss of the absorber water and the lamp wells (rupture, ignition in a
  flammable toluene atmosphere) are open items, and the process is public with
  CC-BY-4.0, every library entry is (ADR 0036);
- (core 1.9.0, ADR 0060) the toluene recycle S2 is a tear stream converged by propagate, not an
  assumed stream, at the splitter's 0.98;
- (core 1.10.0, ADR 0061) the forerun ST102 and the main cut ST103 run through the still's
  column: their reboilers and condensers are the models' `(R + 1)` times the distillate's latent
  heat, the product is 99.85 wt%, and the sensible heat core leaves out is the recorded
  exclusion of D-009, recomputed here from scripts/balance.py;
- (core 1.10.0, ADR 0062) R101's vent carries the content's vapour through E-102 as its vent
  condenser, whose duty is the model's on Q4; the hand streams Q12 and Q13 are gone; R101's model
  duty runs into the content and the jacket Q2 is the light and the agitator less it; E-103 is
  the script's flash of S7 at 268.15 K, and the vapour by hand on the charge and the crude is
  the model's start and end;
- (core 1.10.0, ADRs 0058, 0062) R-101's off-gas capacity covers the gas and vapour released at
  the MTSR in the design case with the stated margin; the slow cases and the blocked vent stay
  open findings (D-014).
"""

from __future__ import annotations

import importlib.util
import math
import re
from pathlib import Path

import pytest
import yaml

KIT = Path(__file__).resolve().parents[1]
PROCESS = KIT / "processes" / "benzyl-bromide-1"
BATCHES = 1127.02  # cheme process recipe (D-003)


def _yaml(rel: str) -> dict:
    return yaml.safe_load((PROCESS / rel).read_text(encoding="utf-8"))


def _text(rel: str) -> str:
    return " ".join((PROCESS / rel).read_text(encoding="utf-8").split())


@pytest.fixture(scope="module")
def model():
    materials = {c["id"]: c for c in _yaml("process/materials.yaml")["components"]}
    streams = {s["id"]: s for s in _yaml("process/flowsheet.yaml")["streams"]}
    return materials, streams


@pytest.fixture(scope="module")
def balance():
    """scripts/balance.py as a module (its functions and its main's values)."""
    spec = importlib.util.spec_from_file_location("bnbr_balance", PROCESS / "scripts" / "balance.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _steps() -> dict:
    return {s["id"]: s for s in _yaml("process/flowsheet.yaml")["steps"]}


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


def _latent(model, sid: str) -> float:
    return sum(n * model[0][k]["heat_of_vaporization"] for k, n in _kmol(model, sid).items() if n)


def _temperature(model, sid: str) -> float:
    return _state(model, sid)["temperature"]["value"]


def _duty(model, sid: str) -> float:
    return _state(model, sid)["duty"]["value"]


def test_yields_and_assay_follow_from_the_flowsheet(model):
    product = _kmol(model, "S15")["BNBR"]
    assert product / _kmol(model, "S5")["BR2"] == pytest.approx(0.9024, abs=5e-4)
    assert product / _kmol(model, "S1")["TOL"] == pytest.approx(0.8767, abs=5e-4)
    masses = _kg(model, "S15")
    assert masses["BNBR"] / sum(masses.values()) == pytest.approx(0.9985, abs=5e-5)
    assert masses["BALBR"] / sum(masses.values()) == pytest.approx(0.0004, abs=5e-5)
    for rel in ("DESIGN.md", "process.yaml"):
        text = _text(rel)
        assert "90.2 %" in text and "87.7 %" in text and "99.85 wt%" in text, rel
    rate = _state(model, "S15")["flow"]["value"]
    assert _state(model, "S5")["flow"]["value"] / rate == pytest.approx(1.034, abs=5e-4)
    assert _state(model, "S1")["flow"]["value"] / rate == pytest.approx(0.614, abs=5e-4)


def test_the_assay_and_the_yield_carry_their_caveats(model):
    """The assay is an upper bound (by-products not modelled) everywhere it is stated, and the
    modelled yield on toluene is said to stay below the source's 90 %."""
    manifest = _yaml("process.yaml")
    assert "upper bound" in " ".join(manifest["description"].split())
    note = next(o for o in manifest["chemistry"]["outputs"] if o["inventory_key"] == "product:BNBR")
    assert "upper bound" in note["note"]
    assert "upper bound" in _yaml("process/design-basis.yaml")["products"][0]["purity"]
    assert "upper bound" in _text("README.md")
    design = _text("DESIGN.md")
    assert "The 99.85 wt% is an upper bound" in design
    assert "The modelled yield on toluene is below the source's" in design
    # SRC-1, Example I: about 90 % on toluene; the flowsheet's yield on the toluene make-up
    assert _kmol(model, "S15")["BNBR"] / _kmol(model, "S1")["TOL"] < 0.90


def test_acid_strength_and_the_allocation_shares(model):
    acid = _kg(model, "S11")
    assert acid["HBR"] / (acid["HBR"] + acid["H2O"]) == pytest.approx(0.48, abs=1e-4)
    # the vent's toluene and bromine stay in the acid in the model (D-008)
    total = sum(acid.values())
    assert acid["TOL"] / total == pytest.approx(0.0033, abs=1e-4)
    assert acid["BR2"] / total == pytest.approx(0.0032, abs=1e-4)
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
    splitter = _steps()["SP201"]
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
    t17 = _mix(
        model,
        ("S12", _temperature(model, "S12")),
        ("S14", _temperature(model, "S14")),
        ("S19", _temperature(model, "S19")),
    )
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
    # the vent gas, its condensate and the forerun leave the brine coolers above bromine's
    # 265.95 K melting point
    for sid in ("S9", "S14", "S19"):
        assert _temperature(model, sid) > 265.95 + 2.0, sid


def test_every_energy_flow_reaches_the_lci(model):
    _, streams = model
    energy = [s for s in streams.values() if s.get("kind") == "energy"]
    rate = _state(model, "S15")["flow"]["value"]
    by_sink = {}
    for s in energy:
        by_sink.setdefault(s["to"].split(".")[0], []).append(s["id"])
        by_sink.setdefault(s["from"].split(".")[0], []).append(s["id"])
    assert set(by_sink["CW"]) == {"Q2", "Q3", "Q4", "Q6", "Q8", "Q11", "Q15"}
    assert set(by_sink["BRINE"]) == {"Q5", "Q10", "Q16"}
    assert set(by_sink["LPS"]) == {"Q1", "Q7", "Q9", "Q14"}
    assert set(by_sink["POWER"]) == {"P1", "P2", "P3"}
    per_kg = {k: sum(_duty(model, q) for q in v) / rate for k, v in by_sink.items() if k in ("CW", "BRINE", "LPS", "POWER")}
    assert per_kg["CW"] == pytest.approx(0.666, abs=5e-4)
    assert per_kg["BRINE"] == pytest.approx(0.046, abs=5e-4)
    assert per_kg["LPS"] == pytest.approx(0.431, abs=5e-4)
    assert per_kg["POWER"] == pytest.approx(0.1595, abs=5e-4)
    design, manifest = _text("DESIGN.md"), _text("process.yaml")
    for figure in ("0.666 kWh", "0.046 kWh", "0.431 kWh", "0.160 kWh"):
        assert figure in design and figure in manifest, figure
    inventory = {row.split(",")[0]: row for row in (PROCESS / "lca" / "inventory.csv").read_text(encoding="utf-8").splitlines()[1:]}
    assert {"product:CW", "product:BRINE", "feed:LPS", "feed:POWER"} <= set(inventory)
    assert inventory["product:CW"].endswith(",Q2 Q3 Q4 Q6 Q8 Q11 Q15")
    assert inventory["product:BRINE"].endswith(",Q5 Q10 Q16")
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
    assert batches == pytest.approx(BATCHES, abs=0.2)  # D-003
    assert recipe["unit_procedures"][1]["units"] == ["ST101", "ST102", "ST103"]


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


def _per_batch(model, sid: str) -> dict[str, float]:
    cycle = _yaml("process/recipe.yaml")["hours_per_year"]["value"] / BATCHES
    return {k: n * cycle for k, n in _kmol(model, sid).items() if k != "HBR"}


def test_the_mtt_is_below_the_content_bubble_point_in_the_design_case(model):
    materials, _ = model
    hazard = _steps()["R101"]["hazard"]
    end = {k: v for k, v in _state(model, "S6")["composition"]["values"].items() if v and k != "HBR"}
    # the worst moment: the end of the dosing with 1.66 % of the bromine dosed unreacted
    x_br2 = 0.0166 * sum(_per_batch(model, "S5").values()) / sum(_per_batch(model, "S6").values())
    worst = {k: v * (1 - x_br2) for k, v in end.items()}
    worst["BR2"] = x_br2
    assert _bubble(materials, worst) == pytest.approx(393.7, abs=0.3)
    assert hazard["mtt"] < _bubble(materials, worst)
    assert "393.7 K at the worst moment" in _text("DESIGN.md")


def test_the_k100_bromine_fraction_counts_the_liquid_at_the_end_of_dosing(model):
    """At k/100 (accumulation 67.6 %) the bromine left is a share of the whole liquid: the
    charge plus the bromine dosed less one mole per mole reacted (the HBr is vented), not of
    the charge alone."""
    materials, _ = model
    charge, dosed = _per_batch(model, "S4"), _per_batch(model, "S5")["BR2"]
    reacted = (1 - 0.676) * dosed
    liquid = dict(charge)
    liquid["BR2"] = liquid.get("BR2", 0.0) + dosed - reacted
    liquid["TOL"] -= reacted
    liquid["BNBR"] += reacted
    total = sum(liquid.values())
    assert total == pytest.approx(27.78, abs=0.02)
    assert liquid["BR2"] / total == pytest.approx(0.140, abs=1e-3)
    bubble = _bubble(materials, {k: v / total for k, v in liquid.items() if v > 0})
    assert bubble == pytest.approx(372.2, abs=0.5)
    design = _text("DESIGN.md")
    assert "about 14 mol% bromine at the end of the dosing (3.9 kmol in 27.8 kmol of liquid" in design
    assert "about 372 K at k/100" in design
    # above the MTT, so the content boils at the k/100 MTSR (core 1.10.0's `boils`)
    assert "| k/100 | 67.6 % | 396.1 K | 12.3 K above |" in (PROCESS / "DESIGN.md").read_text(encoding="utf-8")


def test_the_lamp_power_source_states_the_lamps_and_hours_the_duty_uses(model):
    """P1 is 20 kW over the 5.24 h of light a batch (dosing and post-reaction), as a year
    average; the source names those, not a rating over the dosing alone."""
    recipe = _yaml("process/recipe.yaml")
    light_h = 18_851.4 / 3600.0  # scripts/balance.py LIGHT_S
    p1 = 20.0 * light_h * BATCHES / recipe["hours_per_year"]["value"]
    assert _duty(model, "P1") == pytest.approx(p1, rel=1e-3)
    source = _state(model, "P1")["duty"]["source"]
    assert "20 kW of lamps" in source and "5.24 h of light" in source
    assert "30 kW" not in _text("process/flowsheet.yaml")
    script = (PROCESS / "scripts" / "balance.py").read_text(encoding="utf-8")
    assert "P_LAMP = 20.0" in script and "LIGHT_S = 18_851.4" in script


def test_the_residue_left_in_c101_and_its_jacket(model):
    """The residue at the end of ST103 is about 0.04 m3, inside C-101's dished bottom, and the
    note and D-007 say the end of the main cut cannot run at the stated boil-up."""
    materials, _ = model
    residue = _per_batch(model, "S16")
    volume = sum(n * materials[k]["liquid_molar_volume"] for k, n in residue.items())
    mass = sum(n * materials[k]["molar_mass"] for k, n in residue.items())
    assert mass == pytest.approx(70.0, abs=0.1)
    assert volume == pytest.approx(0.0434, abs=1e-3)
    assert volume < 0.0998 * 1.62**3  # the DIN 28011 bottom of C-101
    note = _text("equipment/equipment-list.yaml")
    assert "about 0.04 m3 (70.0 kg) is left at the end of ST103, inside the bottom head" in note
    assert "cannot run at the stated 80 kW" in note
    design = _text("DESIGN.md")
    assert "The end of the main cut cannot run at 80 kW." in design
    assert "C-101 is then busy 5.66 h of the 7.03 h cycle" in design


def test_the_lamp_wells_and_flammability_are_open_items():
    design = _text("DESIGN.md")
    assert "(d) The lamp wells and flammability." in design
    for item in ("toluene's flash point of 4 C", "lower explosive limit of 1.1 vol%",
                 "a path apart from the jacket leak of (b)", "O2 check", "air in-leakage into the vacuum stills"):
        assert item in design, item
    equipment = _text("equipment/equipment-list.yaml")
    assert "lamp power tripped on a well-coolant fault" in equipment
    assert "D-011 (d)" in equipment


def test_benzotribromide_bound_matches_its_derivation(model):
    """D-005's bound: benzal bromide's share of the crude over benzyl bromide's, times the share
    of the bromine BALBR takes, below 0.2 % of the bromine (reactions.yaml says so too)."""
    header = (PROCESS / "process" / "reactions.yaml").read_text(encoding="utf-8")
    assert "below 0.2 % of the\n# bromine" in header
    crude = _kmol(model, "S6")
    ratio = crude["BALBR"] / crude["BNBR"]
    assert ratio == pytest.approx(0.033, abs=5e-4)
    balbr = (crude["BALBR"] + _kmol(model, "S7")["BALBR"] - _kmol(model, "S4")["BALBR"]) / _kmol(model, "S7")["HBR"]
    assert balbr == pytest.approx(0.036, abs=5e-4)
    assert ratio * balbr < 0.002
    assert "below 0.2 % of the bromine (0.033 x the 3.6 % that BALBR takes)" in _text("DESIGN.md")


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


def test_published_public_with_cc_by():
    publication = _yaml("process.yaml")["publication"]
    assert publication == {"status": "public", "license": "CC-BY-4.0"}


# core 1.10.0 (ADRs 0061, 0062, with 0058 to 0060 of core 1.9.0)

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


def test_the_column_cuts_and_their_duties(model):
    """ST102 (forerun, reflux 2) and ST103 (main cut, reflux 0.5) run through K-101 (5 stages):
    the reboilers and the condensers are (R + 1) times the distillate's latent heat, written by
    propagate (ADR 0061); the one-stage ST102 with two cuts is gone."""
    steps = _steps()
    for node, ratio in (("ST102", 2), ("ST103", 0.5)):
        still = steps[node]["still"]
        assert still["column"]["stages"] == 5 and still["column"]["reflux"] == "constant", node
        assert still["column"]["ratio"] == ratio and still["condenser_port"] == "q", node
        assert "cuts" not in still and steps[node]["energy_port"] == "steam", node
    assert "column" not in steps["ST101"]["still"] and steps["ST101"]["energy_port"] == "steam"
    energy = _energy(model)
    for reboiler, condenser, node, cut, ratio in (("Q9", "Q10", "ST102", "S14", 2), ("Q14", "Q11", "ST103", "S15", 0.5)):
        boil, cond = energy[reboiler]["state"]["design"]["duty"], energy[condenser]["state"]["design"]["duty"]
        assert boil["provenance"] == "calculated" and f"still duty {node}" in boil["source"], reboiler
        assert cond["provenance"] == "calculated" and f"still condenser duty {node}" in cond["source"], condenser
        assert boil["value"] == pytest.approx((ratio + 1) * _latent(model, cut) / 3600.0, rel=2e-4), reboiler
        assert cond["value"] == pytest.approx(boil["value"], rel=1e-9), condenser
    assert energy["Q10"]["to"].startswith("BRINE.") and energy["Q11"]["to"].startswith("CW.")
    # the forerun returns little benzyl bromide; the main cut holds back the benzal bromide
    pot = _kmol(model, "S13")
    assert _kmol(model, "S14")["TOL"] / pot["TOL"] == pytest.approx(0.989, abs=1e-3)
    assert _kmol(model, "S14")["BNBR"] / pot["BNBR"] == pytest.approx(0.029, abs=1e-3)
    s20 = _kmol(model, "S20")
    assert _kmol(model, "S15")["BNBR"] / s20["BNBR"] == pytest.approx(0.979, abs=1e-3)
    assert _kmol(model, "S15")["BALBR"] / s20["BALBR"] == pytest.approx(0.0062, abs=5e-4)
    assert _per_batch(model, "S15")["BNBR"] * 171.037 == pytest.approx(0.9985 * 887.3, abs=0.5)
    design = _text("DESIGN.md")
    assert "Why the column's 99.85 wt% is adopted over the one stage's 98.3 wt%" in design
    for figure in ("98.54 wt%", "99.43 wt%", "99.87 wt%", "99.81 or 99.87 wt%"):
        assert figure in design, figure
    assert "L-4 (core#173)" in design and "**Resolved in core 1.10.0** (ADR 0061" in design


def test_the_stills_steam_is_the_model_and_the_sensible_heat_is_recorded(model, balance):
    materials, _ = model
    energy = _energy(model)
    q7 = energy["Q7"]["state"]["design"]["duty"]
    assert q7["provenance"] == "calculated" and "still duty ST101" in q7["source"]
    assert q7["value"] == pytest.approx(_latent(model, "S12") / 3600.0, rel=2e-4)
    # the script repeats the strip (one Rayleigh stage, core's data) and core's cut
    strip = balance.rayleigh(materials, _kmol(model, "S6"), 15.0, [("top", lambda x: x.get("TOL", 0.0) <= 0.15)])
    assert sum(strip["top"]["moles"].values()) == pytest.approx(sum(_kmol(model, "S12").values()), rel=2e-4)
    assert balance.condenser(materials, strip["top"], T_CW) / 3600.0 == pytest.approx(_duty(model, "Q8"), rel=2e-3)
    values = balance.main()
    assert values["sens7"] == pytest.approx(-1.51, abs=0.01)
    assert values["sens_col"] == pytest.approx(-1.33, abs=0.01)
    assert -(values["sens7"] + values["sens_col"]) == pytest.approx(2.84, abs=0.01)
    design = _text("DESIGN.md")
    assert "2.84 kW (0.022 kWh/kg) less LP steam" in design
    assert "22.58 kW for ST101 (sensible -1.51) and 18.52 for ST102 with ST103 (-1.33)" in design
    # "5.2 % high" of the LCI's steam: the models' Q7, Q9 and Q14 with the heat-up Q1, as feed:LPS
    lps = sum(_duty(model, q) for q in ("Q1", "Q7", "Q9", "Q14"))
    inventory = (PROCESS / "lca" / "inventory.csv").read_text(encoding="utf-8").splitlines()
    row = next(line for line in inventory if line.startswith("feed:LPS,"))
    assert row.endswith(",Q1 Q7 Q9 Q14")
    assert float(row.split(",kWh/h,")[0].rsplit(",", 1)[1]) == pytest.approx(lps, abs=1e-3)
    assert 2.84 / lps == pytest.approx(0.052, abs=5e-4)
    # still.heat_up (ADR 0063) gives none: both charges enter above their bubble points
    assert _temperature(model, "S6") > _bubble(materials, {k: v for k, v in _state(model, "S6")["composition"]["values"].items() if v}, 15.0)
    assert _temperature(model, "S13") > _bubble(materials, {k: v for k, v in _state(model, "S13")["composition"]["values"].items() if v}, 2.0)
    assert "heat_up" not in str(_yaml("process/flowsheet.yaml")["steps"])
    assert "`still.heat_up` (ADR 0063) on ST101, ST102 and ST103" in design


def test_r101_vent_vapour_and_e102_as_its_vent_condenser(model, balance):
    """R101's vent carries the content's vapour through E-102 (a partial condenser at 303.15 K,
    its condensate returned), whose duty is the model's on Q4; Q12, Q13 and the step E102 are
    gone; the model's duty runs into the content, so R101 has no energy_port, and the jacket Q2 is
    the light and the agitator less it."""
    r101 = _steps()["R101"]
    vent = r101["batch"]["vent"]
    assert vent["components"] == ["HBR"] and "vapour" in vent
    assert {k: vent["condenser"][k] for k in ("temperature", "returns", "energy_port")} == {
        "temperature": 303.15, "returns": "vessel", "energy_port": "e102",
    }
    assert "energy_port" not in r101 and "E102" not in _steps()
    energy = _energy(model)
    assert "Q12" not in energy and "Q13" not in energy
    q4 = energy["Q4"]["state"]["design"]["duty"]
    assert energy["Q4"]["from"] == "R101.e102" and energy["Q4"]["to"] == "CW.e102"
    assert q4["provenance"] == "calculated" and "vent condenser duty R101" in q4["source"]
    assert q4["value"] == pytest.approx(8.78, abs=0.01)
    assert "ideal_gas" in model[0]["HBR"]  # the condenser cools the HBr as a gas
    # past E-102 the gas is saturated at 303.15 K over the condensate: below pure toluene's
    s7 = _kmol(model, "S7")
    assert _temperature(model, "S7") == pytest.approx(T_CW)
    pure = _p_sat(model[0], "TOL", T_CW) / (P_ATM - _p_sat(model[0], "TOL", T_CW))
    assert s7["TOL"] / s7["HBR"] == pytest.approx(0.0497, abs=2e-4) and s7["TOL"] / s7["HBR"] < pure
    # the model's vapour is Raoult by hand at the start (the charge) and the end (the crude)
    assert _carried(model, "S4") == pytest.approx(1.07, abs=0.01)
    assert _carried(model, "S6") == pytest.approx(0.66, abs=0.01)
    design = _text("DESIGN.md")
    assert "0.87 mol per mol of HBr over the batch (1.07 at the start, 0.66 at the end)" in design
    assert "The model's vapour differs from the hand value of core 1.9.0, and why." in design
    assert "2.86 mol of toluene per mol of bromine" in design  # ADR 0062's scratch copy
    # R-101's heat (D-009): the model takes in 2.52 kW, which the light and the agitator supply
    values = balance.main()
    assert values["model_in"] == pytest.approx(2.520, abs=2e-3)
    light = 0.3 * _duty(model, "P1")
    assert _duty(model, "Q2") == pytest.approx(light + _duty(model, "P2") - values["model_in"], abs=2e-4)
    assert _duty(model, "P1") == pytest.approx(light + _duty(model, "Q3"), abs=2e-4)
    assert "4.47 + 3.0 - 2.52 = 4.95" in design
    assert "**Mostly resolved in core 1.10.0** (ADR 0062, D-015)" in design


def test_e103_is_the_scripts_flash_of_the_vent_gas(model, balance):
    """E-103 (brine, 268.15 K) is one flash of S7 with the HBr an inert, as core's vent
    condenser: its gas S9 goes to the absorber, its condensate S19 to T-201."""
    materials, _ = model
    s9, s19 = balance.flash(materials, _kmol(model, "S7"), T_VENT, P_ATM)
    for k, n in _kmol(model, "S9").items():
        assert s9.get(k, 0.0) == pytest.approx(n, rel=2e-3, abs=1e-7), k
    for k, n in _kmol(model, "S19").items():
        assert s19.get(k, 0.0) == pytest.approx(n, rel=2e-3, abs=1e-7), k
    assert model[1]["S19"]["to"] == "M201.cond"
    gas = _kmol(model, "S9")
    assert gas["TOL"] / gas["HBR"] == pytest.approx(0.0061, abs=1e-4)
    assert gas["BR2"] / gas["HBR"] == pytest.approx(0.0034, abs=1e-4)
    rate = _state(model, "S15")["flow"]["value"]
    assert _kg(model, "S9")["TOL"] / rate * 1000 == pytest.approx(3.6, abs=0.05)
    assert _kg(model, "S9")["BR2"] / rate * 1000 == pytest.approx(3.5, abs=0.05)
    exclusion = next(e for e in _yaml("lca/lca.yaml")["emission_exclusions"] if e["id"] == "vent-toluene")
    assert "are in the balance" in exclusion["reason"] and "3.6 and 3.5 g per kg" in exclusion["reason"]


def test_the_off_gas_capacity_covers_the_gas_and_vapour_released_at_the_mtsr():
    hazard = _steps()["R101"]["hazard"]
    capacity = hazard["vent_capacity"]
    assert hazard["provenance"] == "assumed" and "1.2 x the largest gas release" in hazard["source"]
    assert "over the batch" in hazard["source"]

    def m3_h(mol_s: float, t: float) -> float:
        return mol_s * 1e-3 * 8.314 * t / P_ATM * 3600.0

    # the non-condensable HBr at the MTSR and the gas with the content's vapour (share 0.418)
    hbr = m3_h(0.32240, 363.949)
    assert hbr == pytest.approx(34.67, abs=0.03)
    release = hbr / (1.0 - 0.41810)
    assert release == pytest.approx(59.57, abs=0.05)
    # the largest over the batch: a cooling failure 0.38 h into the dosing (more toluene, more
    # vapour per mol of HBr; test_core_screens_the_gas_release_at_every_moment repeats it)
    largest = m3_h(0.32141, 363.804) / (1.0 - 0.52556)
    assert largest == pytest.approx(72.80, abs=0.05)
    # the normal peak at the vessel: the recipe's 0.3338 mol/s past E-102 less its toluene and
    # bromine (0.050 and 0.0054 mol per mol of HBr), with 1.03 mol of vapour per mol at T_p
    normal = m3_h(0.3338 / 1.0554, T_REACT) / (1.0 - 0.5073)
    assert normal == pytest.approx(68.9, abs=0.1)
    assert capacity == 5.0 * math.ceil(1.2 * max(release, largest, normal) / 5.0) == 90.0
    table = (PROCESS / "DESIGN.md").read_text(encoding="utf-8").splitlines()
    for name, (stated, ratio) in {"5.0e-4 (design)": (59.57, 0.66), "k/10": (102.3, 1.14)}.items():
        row = next(line for line in table if line.startswith(f"| {name} |"))
        assert f"{stated} m3/h" in row and f"{stated / capacity:.2f} x" in row and f"{ratio:.2f} x" in row, name
    design = _text("DESIGN.md")
    assert "`hazard.vent_capacity: 90`" in design
    assert "72.80 m3/h" in design and "68.9 m3/h" in design
    # the blocked vent: the accumulated bromine's HBr in R-101's 1.20 m3 head space
    head = 4.0 - 2.797
    assert 0.0956 * 8.314 * 363.9 / head / 1000.0 == pytest.approx(0.24, abs=0.005)
    assert 0.882 * 8.314 * 370.3 / head / 1000.0 == pytest.approx(2.26, abs=0.02)
    assert "by about 0.24 MPa at 363.9 K" in design and "by about 2.3 MPa at 370.3 K" in design
    assert "So R-101 needs a relief device" in design
    assert "**The slow cases exceed it.**" in design


def test_core_screens_the_gas_release_within_the_off_gas_capacity():
    pytest.importorskip("chemeascode")
    from chemeascode.domains.safety.reaction_hazards import screen

    report = screen(PROCESS)
    (entry,) = report.entries
    gas = entry.gas_release
    assert gas["per_batch"] and gas["rate_m3_h"] == pytest.approx(59.57, abs=0.05)
    assert gas["vapour_share"] == pytest.approx(0.418, abs=1e-3)
    assert gas["noncondensable_m3_h"] == pytest.approx(34.67, abs=0.05)
    assert gas["vent_capacity_m3_h"] == 90.0 and gas["capacity_ratio"] == pytest.approx(0.662, abs=1e-3)
    assert entry.mtsr == pytest.approx(363.9, abs=0.05)
    assert not [f for f in report.findings if f.level in ("warning", "error")]


def test_core_screens_the_gas_release_at_every_moment():
    """reactor-hazards screens the worst-accumulation moment; the capacity is sized on the
    largest release over the batch: core's own gas release at the MTSR on each moment of R101's
    cooling profile (D-014)."""
    pytest.importorskip("chemeascode")
    import copy

    import chemeascode.domains.process.stirred_tank as tank
    from chemeascode.domains.safety import reaction_hazards as hazards

    solved = {}
    solve = tank.solve_node

    def keep(process, item, inlets, case):
        out = solve(process, item, inlets, case)
        if item.id == "R101":
            solved.update(process=process, item=item, case=case, result=out[0])
        return out

    tank.solve_node = keep
    try:
        (entry,) = hazards.screen(PROCESS).entries
    finally:
        tank.solve_node = solve
    result = solved["result"]
    releases = []
    for point in result.cooling_profile:
        trial = copy.deepcopy(entry)
        trial.gas_release, trial.missing = None, []
        hazards._gas(
            solved["process"], solved["item"], trial, solved["case"], point.moles,
            point.mtsr(None), result.pressure, point.rises, None,
        )
        gas = trial.gas_release
        assert not gas.get("boils")
        releases.append((gas["rate_m3_h"], point.time / 3600.0, gas["vapour_share"]))
    rate, hours, share = max(releases)
    assert rate == pytest.approx(72.80, abs=0.05) and hours == pytest.approx(0.38, abs=0.01)
    assert share == pytest.approx(0.526, abs=1e-3)
    assert rate > entry.gas_release["rate_m3_h"]
    capacity = _steps()["R101"]["hazard"]["vent_capacity"]
    assert capacity == 5.0 * math.ceil(1.2 * rate / 5.0)


def test_requires_core_1_10():
    plant = _yaml("plant.yaml")
    assert plant["requires"] == "cheme-as-code>=1.10"
    for rel in ("README.md", "process.yaml"):
        assert "Needs cheme-as-code 1.10.0" in _text(rel), rel
    design = _text("DESIGN.md")
    assert "## D-015 Core 1.10.0" in design and "## Core features used (core 1.10.0)" in design
