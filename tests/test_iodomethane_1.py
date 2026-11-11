"""iodomethane-1 (#163): the folder's stated numbers against its own flowsheet.

The flowsheet's streams (propagated by core and given by scripts/balance.py) are read as YAML,
and the statements the folder makes in DESIGN.md, README.md and process.yaml are checked against
them:

- the feed ratios are CN 114195616 B, Example 1's, and the by-product is phosphorous acid
  (D-004); the heat of reaction follows from the formation enthalpies it cites (D-005);
- the yield on the iodine (95.01 %, inside the source's 95-96 %, stated as an upper bound),
  the specific iodine and methanol, and the iodine's fate, which closes (D-013);
- core 1.10.0 (D-010, D-016): ST102 is core's batch rectification with its column (5 stages at a
  reflux ratio of 2) and its charge's heat-up; its purity (99.86 wt%, above the source's 99.5-99.7
  %, recorded as a finding, not a design claim: a rigorous column on the ideal liquid gives at
  least the shortcut's, the real liquid may give less) and recovery are the model's; one stage
  gives 99.40 wt%, below the source; the reboiler Q8 and the condenser Q10 are the model's duties;
  the specified split K104, its return and the hand streams Q9 and Q13 are gone; ST102's heat-up
  is timed in the recipe at the reboiler's duty; ST101's heat-up stays by hand because core 1.10.0
  refuses it, and R101's vent fraction because core's vent vapour would take the vented
  iodomethane, not the nitrogen, as its carrier; the specified splits close on their inlets;
- R101's vent fraction is the one scripts/balance.py estimates, each kmol of nitrogen counted once
  and a displaced head space not saturated twice (D-012);
- the heating medium stays below the patent's 90 C kettle limit, the residue's bubble point
  below the medium, and the jacket check uses the chilled water's log-mean temperature;
- the mixed residue's temperature follows from its inlets;
- the MTT is the source's reflux temperature, core's default is not, and the criticality
  classes DESIGN.md states are the ones core's `criticality()` can give without a TD24;
- the models write Q2, Q3 (core 1.9.0), Q8 and Q10 (core 1.10.0), Q2 is the reaction's heat less
  the iodine warmed, every heat stream reaches the LCI, the per-kg utilities are the stated ones;
- the vent capacity covers its basis and core's gas release; the boil-off at the MTT and the
  jacket changeover case are the stated ones (design finding);
- the batch size, the cycle and the powers follow from the recipe core gives; the still's heat-up
  takes time, ST101's net boil-up leaves the residue's sensible heat its share of the jacket, and
  V-102 receives the crude while ST101 distils it (D-003, D-007);
- the MTT is the measured reflux temperature, reconciled with the ideal liquid's bubble point;
  the stills' temperatures are the script's, not ST101's (D-006, D-007);
- the release cases include the loss of agitation during the solid dose (D-006 (g));
- the process is public with CC-BY-4.0, every library entry is (ADR 0036), and needs core 1.10.
"""

from __future__ import annotations

import importlib.util
import math
import re
from pathlib import Path

import pytest
import yaml

KIT = Path(__file__).resolve().parents[1]
PROCESS = KIT / "processes" / "iodomethane-1"
R_GAS = 8.314


def _load(rel: str) -> dict:
    return yaml.safe_load((PROCESS / rel).read_text(encoding="utf-8"))


MATERIALS = {c["id"]: c for c in _load("process/materials.yaml")["components"]}
MW = {n: c["molar_mass"] for n, c in MATERIALS.items()}


@pytest.fixture(scope="module")
def sheet() -> dict:
    return _load("process/flowsheet.yaml")


@pytest.fixture(scope="module")
def streams(sheet) -> dict[str, dict]:
    return {s["id"]: s["state"]["design"] for s in sheet["streams"] if "state" in s}


def _components(state: dict) -> dict[str, float]:
    """kg/h of each component (flow kg/h; mole or mass fractions)."""
    comp, flow = state["composition"], state["flow"]["value"]
    if comp["basis"] == "mass_fraction":
        return {n: flow * x for n, x in comp["values"].items()}
    mean = sum(x * MW[n] for n, x in comp["values"].items())
    return {n: flow * x * MW[n] / mean for n, x in comp["values"].items()}


def _text(rel: str) -> str:
    return " ".join((PROCESS / rel).read_text(encoding="utf-8").split())


def _step(sheet, sid: str) -> dict:
    return next(s for s in sheet["steps"] if s["id"] == sid)


def _balance():
    spec = importlib.util.spec_from_file_location("mei_balance", PROCESS / "scripts" / "balance.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _psat(name: str, t: float) -> float:
    vp = MATERIALS[name]["vapour_pressure"]
    return 100.0 * 10.0 ** (vp["a"] - vp["b"] / (t + vp["c"]))


def test_the_feed_ratios_are_the_sources_and_the_by_product_is_phosphorous_acid(streams):
    i2 = _components(streams["S5"])["I2"] / MW["I2"]
    meoh = _components(streams["S1"])["MEOH"] / MW["MEOH"]
    p = _components(streams["S2"])["P"] / MW["P"]
    # CN 114195616 B, Example 1: 144 kg methanol (99.5 %), 36 kg red P (98.5 %), 360 kg iodine (95 %)
    ex1 = (144 * 0.995 / 32.042, 36 * 0.985 / 30.974, 360 * 0.95 / 253.808)
    assert meoh / i2 == pytest.approx(ex1[0] / ex1[2], rel=1e-4) == pytest.approx(3.319, abs=1e-3)
    assert p / i2 == pytest.approx(ex1[1] / ex1[2], rel=1e-4) == pytest.approx(0.8496, abs=1e-4)
    reaction = next(r for r in _load("process/reactions.yaml")["reactions"] if r["id"] == "MEI")
    assert reaction["stoichiometry"] == {"MEOH": -6, "P": -2, "I2": -3, "MEI": 6, "H3PO3": 2}
    # the excess of phosphorus at both stoichiometries (D-004)
    assert p / i2 > 2 / 3 > 2 / 5
    assert "phosphorous acid (H3PO3), not the phosphoric acid (H3PO4)" in _text("DESIGN.md")


def test_the_heat_of_reaction_follows_from_the_cited_formation_enthalpies():
    # CRC via chemicals 1.5.2: methanol (l) -239.2, iodomethane (l) -13.6, H3PO3 (cr) -964.4; red P -17.6
    heat = 6 * -13.6 + 2 * -964.4 - 6 * -239.2 - 2 * -17.6
    assert heat == pytest.approx(-540.0, abs=1e-6)
    reaction = next(r for r in _load("process/reactions.yaml")["reactions"] if r["id"] == "MEI")
    assert reaction["heat_of_reaction"]["value"] == pytest.approx(heat * 1000.0)
    assert heat + 2 * 12.8 == pytest.approx(-514.4)  # liquid phosphorous acid
    # the patent's equation per mol of iodine, liquid phosphoric acid (D-004)
    h3po4 = (10 * -13.6 + 2 * -1271.7 + 2 * -285.8 - 10 * -239.2 - 2 * -17.6) / 5
    assert h3po4 == pytest.approx(-164.8, abs=0.05)
    assert "(-180 against -165 kJ per mol I2 by SRC-4)" in _text("DESIGN.md")


def test_the_yield_and_the_specific_feeds_follow_from_the_flowsheet(streams):
    i_fed = 2.0 * _components(streams["S5"])["I2"] / MW["I2"]
    product = _components(streams["S25"])
    yield_i = product["MEI"] / MW["MEI"] / i_fed
    assert yield_i == pytest.approx(0.9501, abs=5e-5)
    # an upper bound inside the source's 95, 96 and 95.6 % (the losses not modelled lower it)
    assert 0.95 <= yield_i < 0.96
    for rel in ("DESIGN.md", "README.md", "process.yaml"):
        assert "95.01 %" in _text(rel), rel
    assert "ASSUMED upper bound" in _text("DESIGN.md") and "ASSUMED upper bound" in _text("README.md")
    total = streams["S25"]["flow"]["value"]
    assert streams["S5"]["flow"]["value"] / total == pytest.approx(0.9416, abs=5e-4)
    assert streams["S1"]["flow"]["value"] / total == pytest.approx(0.3939, abs=5e-4)
    meoh = _components(streams["S1"])["MEOH"] / MW["MEOH"]
    assert product["MEI"] / MW["MEI"] / meoh == pytest.approx(0.573, abs=0.005)
    assert "On methanol the yield is 57 %" in _text("DESIGN.md")


def test_the_iodines_fate_closes_and_is_the_stated_one(streams):
    i_fed = 2.0 * _components(streams["S5"])["I2"] / MW["I2"]
    c = {s: _components(streams[s]) for s in ("S7", "S9", "S16", "S19", "S23", "S25")}
    fate = {
        "product": c["S25"]["MEI"] / MW["MEI"],
        "residue": c["S9"].get("MEI", 0.0) / MW["MEI"] + 2 * c["S9"].get("I2", 0.0) / MW["I2"],
        "final": c["S23"]["MEI"] / MW["MEI"],
        "washes": (c["S16"].get("MEI", 0.0) + c["S19"].get("MEI", 0.0)) / MW["MEI"],
        "iodide": c["S16"].get("NAI", 0.0) / MW["NAI"],
        "vent": c["S7"]["MEI"] / MW["MEI"],
    }
    assert sum(fate.values()) / i_fed == pytest.approx(1.0, abs=5e-5)
    stated = {"residue": 0.0140, "final": 0.0235, "washes": 0.0088, "vent": 0.00357}
    for key, share in stated.items():
        assert fate[key] / i_fed == pytest.approx(share, abs=5e-5), key
    design = _text("DESIGN.md")
    assert "ST101's residue 1.40 %" in design and "the final residue 2.35 %" in design
    assert "the wash liquors 0.88 %" in design and "the adsorber 0.36 %" in design
    losses = 1.0 - (fate["product"] + fate["iodide"]) / i_fed
    assert losses == pytest.approx(0.050, abs=0.001)
    assert "About 5.0 % of the iodine fed" in design


def test_st102_is_cores_batch_rectification_and_the_hand_column_is_gone(sheet, streams):
    """Core 1.10.0 (ADR 0061, 0063; D-016): the still with its column and its charge's heat-up,
    the whole reboiler as its boil-up; K104's specified split, M104, the column's return and the
    typed reflux share and heat-up are gone."""
    still = _step(sheet, "ST102")["still"]
    column = still["column"]
    assert (column["stages"], column["reflux"], column["ratio"]) == (5, "constant", 2)
    assert column["provenance"] == "assumed"
    assert still["heat_up"] is True and still["condenser_port"] == "condenser"
    assert still["boilup"]["value"] == 36 and still["boilup"]["unit"] == "kW"  # the reboiler, not the net 12 kW
    assert still["end"] == {"residue": {"key": "MEI", "mole_fraction": 0.5}}  # unchanged (D-010)
    steps = {s["id"] for s in sheet["steps"]}
    assert not steps & {"K104", "M104"} and "E104" in steps
    ids = {s["id"] for s in sheet["streams"]}
    assert not ids & {"S27", "S28", "Q9", "Q13"}
    flow = {s["id"]: (s["from"], s["to"]) for s in sheet["streams"]}
    assert flow["S22"] == ("ST102.top", "E104.in") and flow["Q10"] == ("ST102.condenser", "CW.k104")
    assert flow["S23"] == ("ST102.bottom", "H103.in")
    assert "K104" not in _load("process/recipe.yaml")["unit_procedures"][3]["units"]


def test_the_columns_purity_and_recovery_are_the_models_and_above_the_source(streams):
    """Regression (D-010, D-016): 5 stages at a reflux of 2 on the ideal liquid give 99.86 wt% at
    97.59 % recovery of the iodomethane, above the source's 99.5-99.7 % (a finding, not a design
    claim: a rigorous column on the same liquid gives at least this, the real liquid may give
    less)."""
    s20, s22, s25 = (_components(streams[s]) for s in ("S20", "S22", "S25"))
    total = sum(s25.values())
    purity = s25["MEI"] / total
    assert purity == pytest.approx(0.99864, abs=2e-5)
    assert purity > 0.997  # above the source's highest, Example 2: a finding, recorded (D-016)
    assert s25["MEOH"] / total == pytest.approx(0.00136, abs=2e-5)
    assert s25["H2O"] / total < 1e-6  # the ideal liquid keeps the water in the pot: optimistic
    assert s22["MEI"] / s20["MEI"] == pytest.approx(0.97585, abs=2e-4)
    assert s22["MEOH"] / s20["MEOH"] == pytest.approx(0.2015, abs=1e-3)
    design = _text("DESIGN.md")
    assert "**99.86 wt% iodomethane, 0.14 wt% methanol and 0.2 ppm water**" in design
    assert "recovering 97.59 % of the iodomethane" in design
    assert "**The model's purity lies above the source's 99.5-99.7 %**" in design
    assert "99.86 wt%" in _text("README.md") and "99.86 wt%" in _text("process.yaml")
    readme = _text("README.md")
    assert "so it is a finding, not a design claim" in readme and "would give at least this" in readme
    assert "so it is a finding, not a design claim" in design
    for text in (design, readme, _text("process.yaml"), _text("equipment/equipment-list.yaml")):
        assert "the ideal liquid's upper bound" not in text and "an upper bound above" not in text


def _st102(stages: int | None = None):
    """Core's batch rectification of ST102 (solve_node), optionally at other stages."""
    pytest.importorskip("chemeascode")
    from chemeascode.domains.process.batch_still import inlets_of, solve_node
    from chemeascode.domains.process.model import load

    process, _ = load(PROCESS)
    case = process.flowsheet.default_case()
    node = process.nodes["ST102"]
    if stages is not None:
        column = node.still.column.model_copy(update={"stages": stages})
        node = node.model_copy(update={"still": node.still.model_copy(update={"column": column})})
    result, _ = solve_node(process, node, inlets_of(process, node), case)
    return result


def test_one_stage_is_short_of_the_source_and_the_column_reaches_beyond_it():
    """The column at one stage is the first version's Rayleigh still (99.40 wt%, below the
    source's 99.5 %); the stage sensitivity of D-010."""
    stated = {1: (0.9940, 0.9968), 3: (0.9966, 0.9849), 5: (0.9986, 0.9759), 8: (0.9997, 0.9713)}
    for stages, (purity, recovery) in stated.items():
        result = _st102(stages)
        cut = result.cuts[0].moles
        mass = {n: v * MW[n] for n, v in cut.items()}
        assert mass["MEI"] / sum(mass.values()) == pytest.approx(purity, abs=1e-4), stages
        assert cut["MEI"] / result.charge["MEI"] == pytest.approx(recovery, abs=1e-4), stages
        if stages == 1:
            assert mass["MEI"] / sum(mass.values()) < 0.995  # below the source's lowest, Example 1
    design = _text("DESIGN.md")
    assert "1 stage 99.40 wt% at 99.68 % recovery" in design and "8 stages 99.97 wt% at 97.13 %" in design


def test_the_columns_reboiler_and_condenser_duties_are_the_models(sheet, streams):
    """Regression (ADR 0061, 0063): Q8 is the reboiler, (R + 1) times the distillate's latent heat
    and the charge's heat-up to its bubble point; Q10 the total condenser, the boil-up's latent
    heat only; both calculated by propagate, as core's still solves them."""
    duties = {s["id"]: s["state"]["design"]["duty"] for s in sheet["streams"] if s.get("kind") == "energy"}
    assert duties["Q8"]["provenance"] == "calculated" and "still duty ST102" in duties["Q8"]["source"]
    assert duties["Q10"]["provenance"] == "calculated" and "still condenser duty ST102" in duties["Q10"]["source"]
    result = _st102()
    hours = result.hours
    assert duties["Q10"]["value"] == pytest.approx(result.energy / hours / 3600.0, rel=1e-4)
    assert duties["Q8"]["value"] == pytest.approx((result.energy + result.heat_up) / hours / 3600.0, rel=1e-4)
    latent = sum(v / MW[n] * MATERIALS[n]["heat_of_vaporization"] for n, v in _components(streams["S22"]).items() if v > 0) / 3600.0
    assert duties["Q10"]["value"] == pytest.approx(3.0 * latent, rel=1e-3)  # (R + 1) D lambda
    balance = _balance()
    s20 = _components(streams["S20"])
    t_bubble = balance.bubble_point({n: v / MW[n] for n, v in s20.items()})
    heat_up = sum(v / MW[n] * MATERIALS[n]["liquid_heat_capacity"] for n, v in s20.items()) * (t_bubble - streams["S20"]["temperature"]["value"]) / 3600.0
    assert duties["Q8"]["value"] - duties["Q10"]["value"] == pytest.approx(heat_up, rel=2e-3)
    assert duties["Q8"]["value"] == pytest.approx(10.79, abs=0.005) and duties["Q10"]["value"] == pytest.approx(10.59, abs=0.005)
    # the boil-up time at the 36 kW reboiler is the recipe's distillation
    assert result.time / 3600.0 == pytest.approx(RECIPE_H["distil2"], abs=0.01)
    # the condensate's cooling to 303 K is a stream of its own, from its bubble point
    s22 = _components(streams["S22"])
    t22 = streams["S22"]["temperature"]["value"]
    assert t22 == pytest.approx(balance.bubble_point({n: v / MW[n] for n, v in s22.items()}), abs=0.01)
    cp22 = sum(v / MW[n] * MATERIALS[n]["liquid_heat_capacity"] for n, v in s22.items()) / 3600.0
    assert duties["Q14"]["value"] == pytest.approx(cp22 * (t22 - 303.15), rel=2e-3)
    assert "Q8 10.79 kW of LP steam" in _text("DESIGN.md") and "Q10 10.59 kW to cooling water" in _text("DESIGN.md")


def test_st101s_heat_up_is_refused_and_r101s_vent_stays_by_hand(sheet):
    """D-016: core 1.10.0's `still.heat_up` needs Raoult's law (ST101 has a constant relative
    volatility, D-007). Core accepts a vent vapour on R101's vent, but would take the vented
    iodomethane (a condensable product at a hand-written fraction) as its carrier, while the real
    carrier is the purge's and the blanket's nitrogen, which core does not model; the hand vent
    fraction stays."""
    pytest.importorskip("chemeascode")
    from pydantic import ValidationError

    from chemeascode.domains.process.schema import Still

    st101 = _step(sheet, "ST101")["still"]
    assert st101["volatility"]["model"] == "constant" and "heat_up" not in st101
    with pytest.raises(ValidationError, match="heat_up needs volatility raoult"):
        Still.model_validate({**st101, "heat_up": True})
    vent = _step(sheet, "R101")["batch"]["vent"]
    assert vent["components"] == ["MEI"] and "vapour" not in vent and "condenser" not in vent
    duties = {s["id"]: s["state"]["design"]["duty"] for s in sheet["streams"] if s.get("kind") == "energy"}
    assert duties["Q4"]["provenance"] == "assumed" and duties["Q7"]["provenance"] == "assumed"
    design = _text("DESIGN.md")
    d016 = design[design.index("## D-016") : design.index("## Method and dependency table")]
    assert "core 1.10.0 accepts it on R101's vent" in d016
    assert "as the vapour's carrier" in d016 and "nitrogen" in d016
    assert "schema error" not in design and "R101 forms none" not in design
    assert "**resolved by core 1.10.0** (ADR 0061, `still.column`; D-016)" in design
    assert "**Not resolved by core 1.10.0** (D-016)" in design and "**open for ST101**" in design


@pytest.mark.parametrize(
    ("inlets", "outlets"),
    [(("S14",), ("S15", "S16")), (("S15", "S17"), ("S18", "S19")), (("S18",), ("S20", "S21"))],
)
def test_the_specified_splits_close_on_their_inlets(streams, inlets, outlets):
    names = set()
    for s in inlets + outlets:
        names |= set(_components(streams[s]))
    for name in names:
        into = sum(_components(streams[s]).get(name, 0.0) for s in inlets)
        out = sum(_components(streams[s]).get(name, 0.0) for s in outlets)
        assert out == pytest.approx(into, rel=1e-3, abs=2e-4), name


def test_the_washes_take_the_methanol_down_as_stated(streams):
    share = {s: _components(streams[s]).get("MEOH", 0.0) / streams[s]["flow"]["value"] for s in ("S10", "S15", "S18")}
    assert [round(share[s] * 100, 2) for s in ("S10", "S15", "S18")] == [7.65, 2.95, 0.66]
    assert "methanol in the crude 7.65 -> 2.95 -> 0.66 wt%" in _text("DESIGN.md")


def test_the_vent_fraction_is_the_scripts_estimate(sheet, capsys, monkeypatch):
    monkeypatch.delenv("BALANCE_OUTPUT", raising=False)
    pytest.importorskip("chemeascode")
    _balance().main()
    out = capsys.readouterr().out
    found = re.search(r"vent fraction for R101 \(written by hand\): ([\d.]+)", out)
    assert found, out
    stated = _step(sheet, "R101")["batch"]["vent"]["fraction"]["MEI"]
    assert stated == pytest.approx(float(found.group(1)), rel=1e-3)
    assert f"{stated * 100:.4f} %" in _text("DESIGN.md")


def test_heating_media_stay_below_the_limits_and_the_jacket_uses_the_log_mean():
    jacket = _load("process/recipe.yaml")["unit_procedures"][0]["vessel"]["jacket"]
    supply, back = 363.15, 358.15  # the hot-water loop (D-003)
    assert jacket["heating_temperature"] == pytest.approx((supply + back) / 2)
    assert supply <= 273.15 + 90.0  # CN 114195616 B's kettle limit
    assert supply < 473.0 and supply < 273.15 + 240.0  # phosphorous acid, red phosphorus (D-006)
    lmtd = (35.0 - 30.0) / math.log(35.0 / 30.0)  # chilled water 278.15 -> 283.15 K against 313.15 K
    assert jacket["coolant_temperature"] == pytest.approx(313.15 - lmtd, abs=0.01)


def test_the_residues_bubble_point_stays_below_the_hot_water_supply(streams):
    balance = _balance()
    t9 = balance.bubble_point({n: v / MW[n] for n, v in _components(streams["S9"]).items()})
    assert t9 == pytest.approx(streams["S9"]["temperature"]["value"], abs=0.05)
    assert t9 < 363.15
    assert "357.1 K, below the loop's 363.15 K supply" in _text("DESIGN.md")


def test_mixed_temperatures_follow_from_their_inlets(streams):
    # ST102's residue at its bubble point, as the still ends
    balance = _balance()
    s23 = _components(streams["S23"])
    assert streams["S23"]["temperature"]["value"] == pytest.approx(balance.bubble_point({n: v / MW[n] for n, v in s23.items()}), abs=0.01)
    # the adiabatic washes: between the inlets, raised by the stated heats only
    assert 298.15 < streams["S14"]["temperature"]["value"] < 303.15 + 5.0
    assert 298.15 < streams["S18"]["temperature"]["value"] < streams["S14"]["temperature"]["value"]


def test_the_mtt_is_the_sources_reflux_temperature_and_cores_default_is_not(sheet):
    hazard = _step(sheet, "R101")["hazard"]
    assert hazard["mtt"] == 313.15  # Example 1, total reflux at 39-40 C
    assert MATERIALS["MEOH"]["normal_boiling_point"] - hazard["mtt"] == pytest.approx(24.65, abs=0.01)
    assert "24.7 K too high" in _text("DESIGN.md")


def _criticality(mtsr: float, mtt: float, td24: float) -> int:
    """Stoessel's class as core v1.9.0's reaction_hazards.criticality gives it."""
    if td24 < mtsr:
        return 4 if mtt < td24 else 5
    if mtsr < mtt:
        return 1 if mtt < td24 else 2
    return 3


def test_the_stated_criticality_classes_are_those_any_td24_can_give():
    rows = re.findall(
        r"^\| (?:4\.1e-4 \(design\)|k/10|k/100) \| [^|]+ \| ([\d.]+) K \| [^|]+ \| [^|]+ \| [^|]+ \| [^|]+ \| [^|]+ \| ([^|]+) \|$",
        (PROCESS / "DESIGN.md").read_text(encoding="utf-8"),
        flags=re.M,
    )
    assert len(rows) == 3
    for mtsr, stated in rows:
        possible = {_criticality(float(mtsr), 313.15, 290.0 + 0.25 * i) for i in range(1600)}
        assert {int(c) for c in re.findall(r"\d", stated)} == possible, (mtsr, stated)
    assert "between the MTT and the MTSR (313.15 K < TD24 < 322.6 K)" in _text("DESIGN.md")


def test_the_models_write_q2_q3_q8_q10_and_q2_is_the_reactions_heat_less_the_dose(sheet, streams):
    duties = {s["id"]: s["state"]["design"]["duty"] for s in sheet["streams"] if s.get("kind") == "energy"}
    assert _step(sheet, "R101")["energy_port"] == "q"
    assert _step(sheet, "ST101")["energy_port"] == "steam" and _step(sheet, "ST102")["energy_port"] == "steam"
    for qid, source in (("Q2", "semibatch duty R101"), ("Q3", "still duty ST101"), ("Q8", "still duty ST102"), ("Q10", "still condenser duty ST102")):
        assert duties[qid]["provenance"] == "calculated" and source in duties[qid]["source"], qid
    for qid in ("Q1", "Q4", "Q5", "Q6", "Q7", "Q11", "Q12", "Q14"):
        assert duties[qid]["provenance"] == "assumed" and duties[qid]["source"].startswith("scripts/balance.py"), qid
    formed = (_components(streams["S6"])["MEI"] + _components(streams["S7"])["MEI"]) / MW["MEI"]
    released = 540000.0 * formed / 6.0 / 3600.0
    dose = sum(v / MW[n] * MATERIALS[n]["liquid_heat_capacity"] for n, v in _components(streams["S5"]).items()) * 15.0 / 3600.0
    assert duties["Q2"]["value"] == pytest.approx(released - dose, rel=2e-4)
    assert duties["Q2"]["value"] == pytest.approx(11.574, abs=0.005)
    # ST101's net boil-up is its distillate's latent heat (ST102's duties: the column's test)
    latent = lambda sid: sum(v / MW[n] * MATERIALS[n]["heat_of_vaporization"] for n, v in _components(streams[sid]).items() if v > 0) / 3600.0  # noqa: E731
    assert duties["Q3"]["value"] == pytest.approx(latent("S8"), rel=1e-3)


def test_every_heat_stream_reaches_the_lci(streams):
    rows = {r.split(",")[0]: r.split(",") for r in (PROCESS / "lca" / "inventory.csv").read_text(encoding="utf-8").splitlines()[1:]}
    duty = lambda *ids: sum(streams[i]["duty"]["value"] for i in ids)  # noqa: E731
    groups = {
        "feed:LPS": ("Q1", "Q3", "Q4", "Q8"),
        "product:CW": ("Q5", "Q6", "Q10", "Q12", "Q14"),
        "product:CHW": ("Q2",),
        "product:BRINE": ("Q7", "Q11"),
        "feed:POWER": ("P1", "P2", "P3"),
    }
    product = streams["S25"]["flow"]["value"]
    stated = {"feed:LPS": 0.27024, "product:CW": 0.26916, "product:CHW": 0.18333, "product:BRINE": 0.00702, "feed:POWER": 0.08573}
    design = _text("DESIGN.md")
    for key, ids in groups.items():
        assert float(rows[key][5]) == pytest.approx(duty(*ids), abs=1e-3), key
        assert sorted(rows[key][-1].split()) == sorted(ids), key
        assert duty(*ids) / product == pytest.approx(stated[key], abs=5e-5), key
    assert "LP steam 0.2702 kWh, cooling water 0.2692 kWh, chilled water 0.1833 kWh and brine 0.0070 kWh" in design
    assert "electricity 0.0857 kWh" in design


def test_the_exclusions_carry_their_numbers(streams):
    q2 = streams["Q2"]["duty"]["value"]
    i2 = _components(streams["S5"])["I2"] / MW["I2"]
    fusion = i2 * 15520.0 / 3600.0  # chemicals 1.5.2: iodine's heat of fusion
    assert fusion == pytest.approx(1.0, abs=0.05) and fusion / q2 == pytest.approx(0.09, abs=0.005)
    extent = (_components(streams["S6"])["MEI"] + _components(streams["S7"])["MEI"]) / MW["MEI"] / 6.0
    h3po3 = extent * 25600.0 / 3600.0
    assert h3po3 == pytest.approx(0.55, abs=0.01) and h3po3 / q2 == pytest.approx(0.048, abs=0.001)
    design = _text("DESIGN.md")
    assert "1.0 kW, 9 % of Q2" in design and "0.55 kW, 4.8 % of Q2" in design


# the design case and the scratch copies (k/10, k/100) of 2026-11-06, rerun on core 1.10.0 with
# D-016's batch: core's screening (MTSR, gas at the MTSR) and the boil-off at the MTT (core's
# cooling profile, the rate law at 313.15 K)
SENSITIVITY = {
    "design": {"mtsr": 322.6, "gas": 0.192, "boil": (25.8, 52.9), "m3": (84, 172)},
    "k/10": {"mtsr": 378.7, "gas": 5.40, "boil": (22.4, 49.6), "m3": (73, 161)},
    "k/100": {"mtsr": 603.8, "gas": 6.99e3, "boil": (14.9, 42.1), "m3": (49, 137)},
}


def test_the_boil_off_and_the_vent_are_stated_consistently(sheet):
    capacity = _step(sheet, "R101")["hazard"]["vent_capacity"]
    assert capacity == 20.0
    purge = 5.0 / 22.414 / 0.5 * R_GAS * 313.15 / 101.325  # 5 Nm3 in 0.5 h at 313 K
    assert purge == pytest.approx(11.5, abs=0.05) and purge < capacity
    design = _text("DESIGN.md")
    for case, row in SENSITIVITY.items():
        for kw, m3 in zip(row["boil"], row["m3"]):
            assert kw / 28.41 * 3.6 * R_GAS * 313.15 / 101.325 == pytest.approx(m3, abs=1.0), case
        label = "4.1e-4 (design)" if case == "design" else case
        assert re.search(rf"\| {re.escape(label)} \|[^\n]*\| {row['mtsr']:.1f} K \|", design), case
    assert row["gas"] > capacity  # k/100: core's gas release does not stop at the MTT (L-9)
    dose_on, stopped = (kw / 28.41 * 3.6 * R_GAS * 313.15 / 101.325 for kw in SENSITIVITY["design"]["boil"][::-1])
    assert dose_on / capacity == pytest.approx(8.6, abs=0.05) and stopped / capacity == pytest.approx(4.2, abs=0.05)
    assert "4.2 to 8.6 times the vent capacity" in design


def test_the_jacket_changeover_case_is_stated():
    vessel = next(v for v in _recipe_result().vessels if v.procedure == "REACT")
    assert vessel.jacket_area == pytest.approx(3.82, abs=0.005)
    duty = 300 * vessel.jacket_area * (360.65 - 313.15) / 1000.0
    assert duty == pytest.approx(54.4, abs=0.1)
    assert duty + SENSITIVITY["design"]["boil"][0] == pytest.approx(80, abs=0.5)
    assert "300 W/(m2 K) x 3.82 m2 x (360.65 - 313.15) K = 54 kW" in _text("DESIGN.md")
    assert "with the reaction's 26 kW, 80 kW of boil-off" in _text("DESIGN.md")
    # the design duty of E-101 covers the boil-off with the dosing going on
    assert SENSITIVITY["design"]["boil"][1] < 55.0 and "designed for 55 kW" in _text("DESIGN.md")


def test_core_screens_the_reactor_as_stated():
    pytest.importorskip("chemeascode")
    from chemeascode.domains.process.model import load
    from chemeascode.domains.process.recipe import hours_per_batch
    from chemeascode.domains.process.stirred_tank import solve_node
    from chemeascode.domains.safety.reaction_hazards import screen

    report = screen(PROCESS)
    entry = next(e for e in report.entries if e.node == "R101")
    assert entry.mtsr == pytest.approx(322.57, abs=0.05) and entry.mtt == pytest.approx(313.15)
    assert entry.gas_release["rate_m3_h"] == pytest.approx(SENSITIVITY["design"]["gas"], abs=0.005)
    assert entry.gas_release["vent_capacity_m3_h"] == 20.0
    # the boil-off at the MTT with the dosing stopped: the worst moment's content at 313.15 K
    process, _ = load(PROCESS)
    case = process.flowsheet.default_case()
    item = process.nodes["R101"]
    inlets = [s for s in process.flowsheet.streams if s.kind == "material" and (e := process.ends(s)[1]) is not None and e.node == "R101"]
    solved, _ = solve_node(process, item, inlets, case)
    worst = max(solved.cooling_profile, key=lambda p: p.mtsr())
    vol = sum(n * MATERIALS[c]["liquid_molar_volume"] for c, n in worst.moles.items())
    k = 4.1801e6 * math.exp(-60000.0 / (R_GAS * 313.15))
    rate = k * worst.moles["I2"] / vol * (worst.moles["P"] / vol) ** 0.6667 * vol
    kw = rate * 540000.0 * hours_per_batch(process, case)
    assert kw == pytest.approx(SENSITIVITY["design"]["boil"][0], abs=0.05)


RECIPE_H = {"cycle": 23.208, "dose": 10.0, "react": 0.37, "heatup": 0.18, "distil": 8.55, "distil2": 6.83}


def test_the_design_basis_and_the_functional_unit_state_the_model(streams):
    """Review of #409: the design basis and the LCA's functional unit give the batch, the purity
    and the residues the model gives (D-002, D-003, D-010, D-016), not the 1.9.0 calibration."""
    basis = _load("process/design-basis.yaml")
    recipe = _load("process/recipe.yaml")
    assert basis["capacity"]["batch_kg"] == recipe["batch_size"]["value"]
    assert basis["capacity"]["batches_per_year"] == pytest.approx(7920 / RECIPE_H["cycle"], abs=0.05)
    product = streams["S25"]["flow"]["value"]
    s25 = _components(streams["S25"])
    purity = basis["products"][0]["purity"]
    assert f"{100 * s25['MEI'] / product:.2f} wt%" in purity and "99.5 to 99.7 %" in purity
    assert "calibrated" not in purity
    residue = basis["products"][2]["note"]
    assert f"{1000 * streams['S26']['flow']['value'] / product:.0f} g per kg" in residue
    washes = basis["products"][3]["note"]
    assert f"{(streams['S16']['flow']['value'] + streams['S19']['flow']['value']) / product:.2f} kg per kg" in washes
    assumptions = " ".join(basis["assumptions"])
    assert "specified split calibrated" not in assumptions and "K-104, 5 theoretical stages" in assumptions
    unit = _load("lca/lca.yaml")["functional_unit"]["source"]
    assert f"{100 * s25['MEI'] / product:.2f} wt%" in unit and "calibrated" not in unit


def test_the_batch_size_source_states_the_recipes_cycle(streams):
    batch = _load("process/recipe.yaml")["batch_size"]
    found = re.search(r"over the ([\d.]+) batches the ([\d.]+) h cycle allows, 63\.131 kg/h x ([\d.]+) h", batch["source"])
    assert found, batch["source"]
    batches, cycle, again = (float(g) for g in found.groups())
    assert cycle == again == RECIPE_H["cycle"]
    assert 500e3 / batches == pytest.approx(batch["value"], rel=1e-3)
    assert streams["S25"]["flow"]["value"] * cycle == pytest.approx(batch["value"], rel=1e-3)
    assert "1465.15 kg" in _text("DESIGN.md") and "341.3 batches" in _text("DESIGN.md")


def test_the_powers_follow_from_the_recipes_durations(sheet):
    pytest.importorskip("chemeascode")
    from chemeascode.domains.process.model import load
    from chemeascode.domains.process.recipe import evaluate, load_recipe

    process, _ = load(PROCESS)
    recipe, _, _ = load_recipe(PROCESS)
    result = evaluate(process, recipe)
    assert result.cycle_time == pytest.approx(RECIPE_H["cycle"], abs=5e-3)
    hours = {(s.procedure, s.operation): s.end - s.start for s in result.steps}
    assert hours[("REACT", "dose")] == pytest.approx(RECIPE_H["dose"], abs=0.01)
    assert hours[("REACT", "react")] == pytest.approx(RECIPE_H["react"], abs=0.01)
    assert hours[("REACT", "heatup")] == pytest.approx(RECIPE_H["heatup"], abs=0.01)
    assert hours[("REACT", "distil")] == pytest.approx(RECIPE_H["distil"], abs=0.01)
    assert hours[("DISTIL", "distil")] == pytest.approx(RECIPE_H["distil2"], abs=0.01)
    on = sum(hours[("REACT", o)] for o in ("charge", "heat", "dose", "react", "hold", "heatup", "distil", "cool"))
    duties = {s["id"]: s["state"]["design"]["duty"]["value"] for s in sheet["streams"] if s.get("kind") == "energy"}
    assert duties["P1"] == pytest.approx(((3.0 + 0.75) * on + 0.75 * hours[("REACT", "dose")]) / result.cycle_time, abs=1e-3)
    c104 = hours[("DISTIL", "heatup")] + hours[("DISTIL", "distil")] + hours[("DISTIL", "cool")]
    assert duties["P3"] == pytest.approx(((1.5 + 0.75) * c104 + 1.1 * 1.5 + 0.5 * result.cycle_time) / result.cycle_time, abs=1e-3)
    assert f"for {on:.2f} h of each {result.cycle_time:.2f} h cycle" in _text("DESIGN.md")
    vessel = next(v for v in result.vessels if v.procedure == "REACT")
    assert vessel.volume == pytest.approx(1.6) and vessel.peak_duty < vessel.removable


def _recipe_result():
    pytest.importorskip("chemeascode")
    from chemeascode.domains.process.model import load
    from chemeascode.domains.process.recipe import evaluate, load_recipe

    process, _ = load(PROCESS)
    recipe, _, _ = load_recipe(PROCESS)
    return evaluate(process, recipe)


def test_the_stills_heat_up_takes_time_and_the_net_boilup_leaves_room_for_the_residue(sheet, streams):
    """Review of #399: core's `distil from: ST101` times the latent heat only (L-4), so Q4 took no
    time. The recipe heats the mass to its bubble point before the distil, and ST101's boil-up is
    the jacket's 15 kW mean less the residue's sensible heat."""
    react = _load("process/recipe.yaml")["unit_procedures"][0]
    ops = [o["id"] for o in react["operations"]]
    assert ops.index("hold") < ops.index("heatup") == ops.index("distil") - 1
    heatup = next(o for o in react["operations"] if o["id"] == "heatup")
    assert heatup["kind"] == "heat" and "duration" not in heatup  # timed by core from the jacket
    assert heatup["temperatures"] == [313.15, pytest.approx(streams["S8"]["temperature"]["value"], abs=0.005)]
    balance = _balance()
    cp = lambda sid: sum(v / MW[n] * MATERIALS[n].get("liquid_heat_capacity", 0.0) for n, v in _components(streams[sid]).items()) / 3600.0  # noqa: E731
    t8, t9 = streams["S8"]["temperature"]["value"], streams["S9"]["temperature"]["value"]
    first, residue = cp("S6") * (t8 - 313.15), cp("S9") * (t9 - t8)
    duties = {s["id"]: s["state"]["design"]["duty"]["value"] for s in sheet["streams"] if s.get("kind") == "energy"}
    assert first + residue == pytest.approx(duties["Q4"], rel=2e-3)
    boilup = _step(sheet, "ST101")["still"]["boilup"]["value"]
    assert boilup == pytest.approx(balance.JACKET_MEAN_ST101 * duties["Q3"] / (duties["Q3"] + residue), abs=0.005)
    result = _recipe_result()
    hours = {(s.procedure, s.operation): s.end - s.start for s in result.steps}
    # the still's time is its latent and the residue's sensible heat at the jacket's mean
    per_batch = result.cycle_time  # the flowsheet's flows are the recipe's year averages
    assert hours[("REACT", "distil")] == pytest.approx((duties["Q3"] + residue) * per_batch / 15.0, rel=2e-3)
    assert hours[("REACT", "heatup")] > 0.15
    assert "Q4 0.70 kW" in _text("DESIGN.md") and "14.36 kW" in _text("DESIGN.md")


def test_v102_receives_the_crude_while_st101_distils_it():
    """Review of #399: the crude runs through E-101 into the thiosulfate in V-102 during REACT's
    distillation (D-001, D-008), so WASH starts with REACT's hold and receives for as long as
    ST101 distils."""
    wash = _load("process/recipe.yaml")["unit_procedures"][1]
    assert wash["id"] == "WASH" and wash["start"] == {"after": "REACT", "operation": "hold"}
    receive = next(o for o in wash["operations"] if o["id"] == "receive")
    assert receive["kind"] == "distil" and receive["from"] == "ST101"
    result = _recipe_result()
    step = {(s.procedure, s.operation): s for s in result.steps}
    distil, got = step[("REACT", "distil")], step[("WASH", "receive")]
    assert got.start == pytest.approx(distil.start, abs=0.01) and got.end == pytest.approx(distil.end, abs=0.01)
    assert step[("WASH", "thiosulfate")].start == pytest.approx(step[("REACT", "hold")].start)
    unit = next(u for u in result.units if u.procedure == "WASH")
    assert unit.utilisation == pytest.approx(0.915, abs=0.005) and unit.occupancy < result.cycle_time
    assert result.makespan == pytest.approx(43.16, abs=0.01)
    design = _text("DESIGN.md")
    assert "V-102 is occupied 91 % of the cycle" in design and "one batch takes 43.16 h" in design


def test_st102s_heat_up_is_timed_at_the_reboilers_duty(sheet):
    """Review of #409: core's `still.heat_up` adds ST102's charge heat-up to the duty Q8, not to
    the still's time (ADR 0063), so DISTIL times it by hand: core's heat-up energy per batch at the
    still's 36 kW boil-up, before the distillation; C-104's agitator and loop run through it (P3)."""
    distil = _load("process/recipe.yaml")["unit_procedures"][3]
    ops = [o["id"] for o in distil["operations"]]
    assert distil["id"] == "DISTIL" and ops.index("heatup") == ops.index("distil") - 1
    heatup = next(o for o in distil["operations"] if o["id"] == "heatup")
    assert heatup["kind"] == "heat" and heatup["duration"]["provenance"] == "calculated"
    kwh = _st102().heat_up / 3600.0  # kJ per batch to kWh
    assert kwh == pytest.approx(4.526, abs=5e-3)
    boilup = _step(sheet, "ST102")["still"]["boilup"]["value"]
    assert heatup["duration"]["value"] == pytest.approx(kwh / boilup, abs=5e-4)
    hours = {(s.procedure, s.operation): s.end - s.start for s in _recipe_result().steps}
    assert hours[("DISTIL", "heatup")] == pytest.approx(kwh / boilup, abs=5e-4)
    design = _text("DESIGN.md")
    assert "**partly resolved by core 1.10.0 for ST102**" in design and "8.46 h" in design


def test_the_vent_counts_each_kmol_of_nitrogen_once(sheet, streams):
    """Review of #399: a displaced head space over the crude at 303 K is already saturated, so it
    is not inert gas to be saturated again; the work-up's blanket is the make-up of the volumes
    its liquids vacate, counted once (D-012)."""
    balance = _balance()
    result = _recipe_result()
    cycle = result.cycle_time
    flows = {s: _components(streams[s]) for s in ("S1", "S2", "S6", "S10", "S13", "S17", "S18", "S20", "S25")}
    s3 = {n: flows["S1"].get(n, 0.0) + flows["S2"].get(n, 0.0) for n in set(flows["S1"]) | set(flows["S2"])}
    workup = sum(balance.volume(flows[s]) for s in ("S10", "S13", "S17", "S18", "S20", "S25")) * cycle
    rise = (balance.volume(flows["S6"]) - balance.volume(s3)) * cycle
    p, t = balance.P, balance.T_COND
    p_in, p_out = balance.psat_mei_low(t), balance.psat_mei_low(balance.T_VENT)
    blanket = 5.0 / 22.414
    assert p * workup / (R_GAS * t) < blanket  # the blanket covers the make-up of the vacated head spaces
    n_wet = blanket + p * rise / (R_GAS * t) * (p - p_in) / p
    formed = (flows["S6"]["MEI"] + _components(streams["S7"])["MEI"]) / MW["MEI"] * cycle
    fraction = n_wet * p_out / (p - p_out) / formed
    assert _step(sheet, "R101")["batch"]["vent"]["fraction"]["MEI"] == pytest.approx(fraction, rel=2e-3)
    # the first version's double count: the displaced volume as nitrogen on top of the blanket
    doubled = (blanket + p * (workup + rise) / (R_GAS * t)) * p_out / (p - p_out) / formed
    assert doubled > 1.6 * fraction
    carbon = next(c for c in _load("lca/lca.yaml")["consumables"] if c["id"] == "activated-carbon")
    assert carbon["per_batch"] == pytest.approx(n_wet * p_out / (p - p_out) * MW["MEI"] / 0.2, abs=0.1)


def test_the_mtt_is_the_measured_reflux_temperature_and_the_stills_temperatures_are_the_scripts(sheet, streams):
    """Review of #399: the MTT (the source's measured reflux temperature) lies 16 K below the
    ideal-liquid bubble point the files use for Q4; the stills' temperatures are the script's."""
    mtt = _step(sheet, "R101")["hazard"]["mtt"]
    t8 = streams["S8"]["temperature"]["value"]
    assert t8 - mtt == pytest.approx(16.4, abs=0.1)
    balance = _balance()
    assert balance.bubble_point({n: v / MW[n] for n, v in _components(streams["S6"]).items()}) == pytest.approx(t8, abs=0.01)
    for sid in ("S8", "S9"):
        source = streams[sid]["temperature"]["source"]
        assert "as ST101 computes" not in source and "gives no temperature" in source, sid
    assert "measured temperature" in _step(sheet, "R101")["hazard"]["source"]
    design = _text("DESIGN.md")
    assert "**measured reflux temperature**, 313.15 K" in design and "329.53 K, 16 K above it" in design
    q4 = next(s for s in sheet["streams"] if s["id"] == "Q4")
    assert f"the residue to {streams['S9']['temperature']['value']:.0f} K" in q4["title"]


def test_the_release_cases_include_the_loss_of_agitation_during_the_dose():
    design = _text("DESIGN.md")
    assert "(g) Accumulation of undissolved iodine: loss of R-101's agitation during the dose" in design
    assert "**the 2.28 % does not cover it**" in design
    assert "on R-101's agitator (case (g))" in design and "never to restart the agitator on an accumulated dose" in design
    assert "agitator running" in _text("equipment/equipment-list.yaml")


def test_the_iodine_feed_cites_iodine_1s_product_stream():
    flakes = next(
        s for s in yaml.safe_load((KIT / "processes" / "iodine-1" / "process" / "flowsheet.yaml").read_text(encoding="utf-8"))["streams"]
        if s["id"] == "S21"
    )
    assert "flakes" in flakes["title"].lower()
    assert "(its product S21)" in _text("DESIGN.md")


def test_published_public_with_cc_by():
    manifest = _load("process.yaml")
    assert manifest["publication"] == {"status": "public", "license": "CC-BY-4.0"}


def test_requires_core_1_10():
    assert _load("plant.yaml")["requires"] == "cheme-as-code>=1.10"
    assert "still.column" in (PROCESS / "plant.yaml").read_text(encoding="utf-8")  # the comment says why
    assert "Needs cheme-as-code 1.10.0" in _text("README.md") and "Needs cheme-as-code 1.10.0" in _text("process.yaml")
    design = (PROCESS / "DESIGN.md").read_text(encoding="utf-8")
    assert "## Core features used (core 1.9.0 and 1.10.0)" in design and "\nCore 1.10.0 (D-016):\n" in design
    assert "## D-016 Core 1.10.0" in design
