"""di-tert-butyl-dicarbonate-1 (#160): the folder's stated numbers against its own flowsheet.

Fast, without running core's models: the flowsheet's streams (propagated by core and given by
scripts/balance.py), the materials' data, the recipe and the LCI's inventory are read as YAML and
CSV, and what the folder states in DESIGN.md, process.yaml and lca/ is checked against them:

- the yields on the alkoxide and on phosgene follow from the streams and stay below the 91.0 %
  the source's Example 1 gives by mass; the assay carries its caveat (an upper bound);
- the recipe's batch size, cycle and batches give 500 t/a and the flowsheet's rate;
- both recycles (the recovered hexane S30 and the paraffin heel S22) are tear streams converged
  by propagate (core ADR 0060), and the charge holds about 5 kg of hexane per kg of carbonate;
- every assumed temperature of a mixed stream is the adiabatic mix of its inlets, the wash stays
  above Boc2O's melting point, and R-101's jacket is checked against the brine's log-mean;
- the heating media stay below the temperature limits the design states (323 K for the strips,
  373 K for the paraffin still), and the stills' ends reach about 313 K;
- every energy flow reaches the LCI: each utility's total per kg is the sum of its energy streams
  and is what DESIGN.md and process.yaml state;
- the criticality classes DESIGN.md states as possible without a TD24 are those core's
  `criticality()` can give with the MTSR below the MTT, and the MTT is the decomposition limit;
- the vent capacity covers the design case's largest cooling-failure release and the k/100 case
  is recorded as exceeding it; water ingress and the loss of the scrubber are discussed;
- tert-butanol-1 is named as the link to make, the process is internal and has no licence;
- (review of PR #401) the hexane that saturates R-101's vent-condenser gas (the dosing's vent S9
  and the degassing's nitrogen sweep) is in the balance and the make-up; the degassing at 30
  kPa(a) needs that sweep, since the slurry's own bubble pressure falls below the still's; the
  dissolved phosgene is stated as stripped into the gas at y = x p*(T) / P, not as boiling off;
  the numbers DESIGN.md quotes follow from the flowsheet; every source id names the register row
  of what it cites; the reboilers deliver their stills' boil-up at the stills' ends.
"""

from __future__ import annotations

import csv
import math
from pathlib import Path

import pytest
import yaml

KIT = Path(__file__).resolve().parents[1]
PROCESS = KIT / "processes" / "di-tert-butyl-dicarbonate-1"


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
    return sum(n * model[0][k].get("liquid_heat_capacity", 0.0) for k, n in _kmol(model, sid).items())


def _temperature(model, sid: str) -> float:
    return _state(model, sid)["temperature"]["value"]


def _duty(model, sid: str) -> float:
    return _state(model, sid)["duty"]["value"]


def test_yields_below_the_source_and_the_assay_an_upper_bound(model):
    product = _kmol(model, "S25")["BOC2O"]
    on_alkoxide = 2 * product / _kmol(model, "S1")["KOTBU"]
    on_phosgene = product / _kmol(model, "S6")["COCL2"]
    assert on_alkoxide == pytest.approx(0.894, abs=5e-4)
    assert on_phosgene == pytest.approx(0.912, abs=5e-4)
    # EP 0 256 559 A2, Example 1: 149 g from 1.5 mol of the alkoxide, purity not stated
    source = 149.0 / (0.75 * 218.249)
    assert source == pytest.approx(0.910, abs=5e-4)
    assert on_alkoxide < source
    masses = _kg(model, "S25")
    assay = masses["BOC2O"] / sum(masses.values())
    assert assay == pytest.approx(0.9998, abs=5e-5)
    for rel in ("DESIGN.md", "process.yaml", "README.md"):
        text = _text(rel)
        assert "89.4 %" in text and "99.98 wt%" in text and "upper bound" in text, rel
    assert "91.0 %" in _text("DESIGN.md") and "91.2 % on phosgene" in _text("DESIGN.md")
    assert "upper bound" in _yaml("process/design-basis.yaml")["products"][0]["purity"]


def test_recipe_gives_the_capacity_and_the_flowsheet_rate(model):
    recipe = _yaml("process/recipe.yaml")
    batch = recipe["batch_size"]["value"]
    rate = _state(model, "S25")["flow"]["value"]
    cycle = batch / rate
    assert cycle == pytest.approx(10.411, abs=2e-3)
    batches = recipe["hours_per_year"]["value"] / cycle
    assert batches == pytest.approx(760.7, abs=0.2)
    assert batch * batches / 1000 == pytest.approx(500.0, abs=0.1)
    for figure in ("657.28 kg", "10.41 h", "760.7 batches"):
        assert figure in _text("DESIGN.md") and figure in _text("process.yaml"), figure


def test_both_recycles_are_tears_converged_by_propagate(model):
    sheet = _yaml("process/flowsheet.yaml")
    assert [t["stream"] for t in sheet["tears"]] == ["S30", "S22"]
    for sid in ("S30", "S22"):
        comp = _state(model, sid)["composition"]
        assert comp["provenance"] == "calculated" and "tear" in comp["source"], sid
    # S30's flow is held (assumed), the splitter SP201 purges the remainder
    assert _state(model, "S30")["flow"]["provenance"] == "assumed"
    assert _state(model, "S36")["flow"]["provenance"] == "calculated"
    s35 = _state(model, "S35")["flow"]["value"]
    assert _state(model, "S30")["flow"]["value"] + _state(model, "S36")["flow"]["value"] == pytest.approx(s35, abs=0.01)
    heel = next(s for s in sheet["steps"] if s["id"] == "SP301")
    assert heel["split"] == {"rec": 0.9}
    # about 5 kg of hexane per kg of the carbonate the alkoxide makes (D-004)
    carbonate = _kmol(model, "S1")["KOTBU"] * model[0]["KTBC"]["molar_mass"]
    assert _kg(model, "S5")["HEX"] / carbonate == pytest.approx(5.0, abs=0.05)


def _mix(model, *sids: str) -> float:
    return sum(_mcp(model, s) * _temperature(model, s) for s in sids) / sum(_mcp(model, s) for s in sids)


def test_mixed_temperatures_and_the_melt(model):
    assert _temperature(model, "S4") == pytest.approx(_mix(model, "S1", "S2", "S3", "S30"), abs=0.01)
    assert _temperature(model, "S23") == pytest.approx(_mix(model, "S19", "S21", "S22"), abs=0.01)
    # the recovered hexane, the purge and the waste solvent: inlets all at 283.15 K
    for sid in ("S13", "S15", "S35", "S30", "S36", "S24", "S37"):
        assert _temperature(model, sid) == pytest.approx(283.15), sid
    # the wash: S16 and S18 mixed less the KCl's heat of solution (+17 kJ/mol), above 296 K
    melt, water = _kmol(model, "S16"), _kmol(model, "S18")
    cp = {k: model[0][k]["liquid_heat_capacity"] for k in melt}
    heat = sum(n * cp[k] for k, n in melt.items()) * _temperature(model, "S16")
    heat += water["H2O"] * 75.3 * _temperature(model, "S18") - melt["KCL"] * 17000.0
    t_wash = heat / (sum(n * cp[k] for k, n in melt.items()) + water["H2O"] * 75.3)
    for sid in ("S19", "S20"):
        assert _temperature(model, sid) == pytest.approx(t_wash, abs=0.01), sid
    assert t_wash > 296.15 + 10
    recipe = _yaml("process/recipe.yaml")
    cool = next(o for o in recipe["unit_procedures"][0]["operations"] if o["id"] == "cool")
    assert cool["temperatures"][0] == pytest.approx(_temperature(model, "S4"), abs=0.01)


def test_jacket_on_the_brine_log_mean_and_heating_media_below_the_limits():
    products = {p["id"]: p for p in _yaml("process/flowsheet.yaml")["products"]}
    brine = products["BRINE"]["utility"]
    t_p = 278.15
    d1 = t_p - brine["supply_temperature"]["value"]
    d2 = t_p - brine["return_temperature"]["value"]
    lmtd = (d1 - d2) / math.log(d1 / d2)
    jacket = _yaml("process/recipe.yaml")["unit_procedures"][0]["vessel"]["jacket"]
    assert jacket["coolant_temperature"] == pytest.approx(t_p - lmtd, abs=0.01)
    steps = {s["id"]: s for s in _yaml("process/flowsheet.yaml")["steps"]}
    for sid in ("ST101", "ST102"):
        assert "321" in steps[sid]["still"]["boilup"]["source"] or "ST101" in steps[sid]["still"]["boilup"]["source"]
    assert "321/316 K" in steps["ST101"]["still"]["boilup"]["source"] and 321 < 323
    assert "368/363 K" in steps["ST301"]["still"]["boilup"]["source"] and 368 < 373
    design = _text("DESIGN.md")
    assert "below 323 K" in design and "373 K" in design


def test_every_energy_flow_reaches_the_lci(model):
    _, streams = model
    energy = [s for s in streams.values() if s.get("kind") == "energy"]
    rate = _state(model, "S25")["flow"]["value"]
    by_terminal: dict[str, list[str]] = {}
    for s in energy:
        for end in (s["from"], s["to"]):
            by_terminal.setdefault(end.split(".")[0], []).append(s["id"])
    assert set(by_terminal["BRINE"]) == {"Q1", "Q2", "Q3"}
    assert set(by_terminal["CHW"]) == {"Q9", "Q16", "Q13"}
    assert set(by_terminal["CW"]) == {"Q14", "Q15"}
    assert set(by_terminal["LPS"]) == {"Q4", "Q5", "Q6", "Q7", "Q8", "Q10", "Q11", "Q12"}
    assert set(by_terminal["POWER"]) == {"P1", "P2", "P3", "P4"}
    with (PROCESS / "lca" / "inventory.csv").open(encoding="utf-8") as fh:
        inventory = {row["key"]: float(row["quantity"]) for row in csv.DictReader(fh)}
    keys = {"BRINE": "product:BRINE", "CHW": "product:CHW", "CW": "product:CW", "LPS": "feed:LPS", "POWER": "feed:POWER"}
    stated = {"BRINE": "0.525", "CHW": "0.925", "CW": "0.125", "LPS": "1.211", "POWER": "0.415"}
    for terminal, key in keys.items():
        per_kg = sum(_duty(model, q) for q in by_terminal[terminal]) / rate
        assert inventory[key] == pytest.approx(per_kg, rel=1e-4), terminal
        assert f"{per_kg:.3f}" == stated[terminal], terminal
        assert f"{stated[terminal]} kWh" in _text("DESIGN.md"), terminal
    # the model duties are core's (ADR 0059), the rest scripts/balance.py's
    for q in ("Q2", "Q5", "Q6", "Q7", "Q11"):
        assert _state(model, q)["duty"]["provenance"] == "calculated", q
    for q in ("Q1", "Q3", "Q4", "Q8", "Q9", "Q10", "Q12", "Q13", "Q14", "Q15", "Q16"):
        assert _state(model, q)["duty"]["source"].startswith("scripts/balance.py"), q


def test_criticality_classes_without_a_td24_and_the_mtt():
    from chemeascode.domains.safety.reaction_hazards import criticality

    mtt = 333.15
    for mtsr in (279.9, 283.7, 294.6):  # design, k/10, k/100 (D-011)
        assert mtsr < mtt
        classes = {criticality(mtsr, mtt, td24) for td24 in (250.0, mtsr - 0.1, mtsr + 1.0, 320.0, 400.0)}
        assert classes == {1, 2, 5}
    design = _text("DESIGN.md")
    assert "class 1 or 2 if the TD24 is at or above the MTSR (1 if it is above the MTT), and class 5 if it is below the MTSR; classes 3 and 4 are excluded" in design
    r101 = next(s for s in _yaml("process/flowsheet.yaml")["steps"] if s["id"] == "R101")
    assert r101["hazard"]["mtt"] == mtt and "not a TD24" in r101["hazard"]["source"]
    assert "td24" not in r101["hazard"]


def test_vent_capacity_and_the_design_findings():
    r101 = next(s for s in _yaml("process/flowsheet.yaml")["steps"] if s["id"] == "R101")
    capacity = r101["hazard"]["vent_capacity"]
    assert capacity == 50
    assert 23.0 / capacity == pytest.approx(0.46, abs=0.005)
    assert 53.5 / capacity == pytest.approx(1.07, abs=0.005)
    design = _text("DESIGN.md")
    for phrase in ("23.0 m3/h", "53.5 m3/h", "1.07", "Water ingress", "Loss of the scrubber", "280.65 K"):
        assert phrase in design, phrase
    # phosgene accumulated at the end of its dosing: 0.0884 kmol of 3.301 kmol a batch (D-011)
    assert 0.0884 / 3.301 == pytest.approx(0.0268, abs=2e-4)


def test_feeds_links_and_publication(model):
    design = _text("DESIGN.md")
    assert "tert-butanol-1" in design and "link the alkoxide's proxy" in design
    proxy_t, proxy_k = 74.123 / 112.213, 39.098 / 112.213
    assert f"{proxy_t:.4f}" == "0.6606" and f"{proxy_k:.4f}" == "0.3484"
    mappings = _yaml("lca/mappings.yaml")["exchanges"]
    assert mappings["feed:PHOS"]["dataset"]["path"] == "processes/phosgene-1/lca/dataset.yaml"
    manifest = _yaml("process.yaml")
    assert manifest["publication"] == {"status": "internal"}
    assert "licence" not in manifest and "license" not in manifest


# --- review of PR #401 -------------------------------------------------------------------------

P_ATM = 101.325
T_VENT_CONDENSER = 263.15  # R-101's vent condenser on brine, gas out (D-006)
T_REACT = 278.15


def _psat(model, component: str, t: float) -> float:
    """kPa, materials.yaml's Antoine line (log10 bar)."""
    vp = model[0][component]["vapour_pressure"]
    return 100.0 * 10 ** (vp["a"] - vp["b"] / (t + vp["c"]))


def _hours(model) -> float:
    return _yaml("process/recipe.yaml")["batch_size"]["value"] / _state(model, "S25")["flow"]["value"]


def _dg101(model) -> dict:
    return next(s for s in _yaml("process/flowsheet.yaml")["steps"] if s["id"] == "DG101")["still"]


def _sweep(model) -> tuple[float, float]:
    """kmol a batch of the degassing's nitrogen and of the hexane that passes the vent condenser
    with it: the slurry boils by itself at the still's pressure down to the CO2 fraction where
    its bubble pressure meets it, then a stripping gas in equilibrium with the liquid takes the
    CO2 to the still's end (y_CO2 = K x, K = p*_CO2 / P)."""
    still = _dg101(model)
    pressure = still["pressure"]
    x_end = still["end"]["residue"]["mole_fraction"]
    feed = _kmol(model, "S10")
    hours = _hours(model)
    liquid = sum(feed.values()) * hours
    co2 = feed["CO2"] * hours
    p_hex = feed["HEX"] / sum(feed.values()) * _psat(model, "HEX", T_REACT)
    k = _psat(model, "CO2", T_REACT) / pressure
    x_self = (pressure - p_hex) / _psat(model, "CO2", T_REACT)
    gas = liquid / k * math.log(x_self / x_end)
    nitrogen = gas * (1.0 - p_hex / pressure) - liquid * (x_self - x_end)
    p_cond = _psat(model, "HEX", T_VENT_CONDENSER)
    hexane = (nitrogen + co2) * p_cond / (pressure - p_cond)
    return nitrogen, hexane


def test_vent_condenser_hexane_is_in_the_balance_and_the_make_up(model):
    """Finding 1: the vent gas S9 leaves R-101's vent condenser saturated with hexane; core's
    batch.vent carries no solvent, so DG101's gas S11 carries it with the degassing's own."""
    hours = _hours(model)
    p_cond = _psat(model, "HEX", T_VENT_CONDENSER)
    assert p_cond == pytest.approx(3.45, abs=0.01)
    n9 = sum(_kmol(model, "S9").values())
    vent_hexane = n9 * p_cond / (P_ATM - p_cond)  # kmol/h
    assert vent_hexane * 86.178 == pytest.approx(1.55, abs=0.01)
    _, sweep_hexane = _sweep(model)
    target = vent_hexane + sweep_hexane / hours
    s11 = _kmol(model, "S11")["HEX"]
    assert s11 == pytest.approx(target, rel=0.02)
    # the hexane leaves to the vent: the scrubbed vent S33 carries it to the oxidiser
    assert _kmol(model, "S33")["HEX"] == pytest.approx(s11, rel=1e-3)
    # the make-up covers what leaves the hexane loop: S11, the stripped melt S16 and the purge S36
    losses = sum(_kg(model, s)["HEX"] for s in ("S11", "S16", "S36"))
    make_up = _state(model, "S2")["flow"]["value"]
    assert make_up == pytest.approx(losses, abs=0.02)
    rate = _state(model, "S25")["flow"]["value"]
    with (PROCESS / "lca" / "inventory.csv").open(encoding="utf-8") as fh:
        inventory = {row["key"]: float(row["quantity"]) for row in csv.DictReader(fh)}
    assert inventory["feed:HEXMU"] == pytest.approx(make_up / rate, rel=1e-4)
    stated = f"{make_up / rate:.3f}"
    assert stated == "0.113"
    assert f"hexane make-up {stated} kg" in _text("DESIGN.md")
    assert f"{stated} kg/kg Boc2O" in _text("process.yaml")
    assert f"{_kg(model, 'S33')['HEX'] / rate:.3f} kg hexane" in _text("DESIGN.md")


def test_degassing_needs_the_nitrogen_sweep(model):
    """Finding 2: at 30 kPa(a) and 278 K the slurry's bubble pressure falls below the still's
    pressure long before 10 ppm CO2; the sweep's nitrogen is a per-batch consumable."""
    still = _dg101(model)
    assert still["pressure"] == 30
    end = _kmol(model, "S12")
    total = sum(end.values())
    bubble = sum(
        n / total * _psat(model, c, T_REACT) for c, n in end.items() if "vapour_pressure" in model[0][c]
    )
    assert bubble < 0.25 * still["pressure"]  # about 6.6 kPa: nothing boils at 30 kPa(a)
    feed = _kmol(model, "S10")
    x_hex = feed["HEX"] / sum(feed.values())
    x_self = (still["pressure"] - x_hex * _psat(model, "HEX", T_REACT)) / _psat(model, "CO2", T_REACT)
    assert x_self == pytest.approx(0.006, abs=3e-4)
    assert feed["CO2"] / sum(feed.values()) > x_self > still["end"]["residue"]["mole_fraction"]
    assert "nitrogen sweep" in still["source"] and "nitrogen sweep" in _text("DESIGN.md")
    nitrogen, _ = _sweep(model)
    assert nitrogen == pytest.approx(2.28, abs=0.03)
    consumable = next(c for c in _yaml("lca/lca.yaml")["consumables"] if c["id"] == "nitrogen")
    assert "DG101's sweep, 2.28 kmol" in consumable["source"]
    assert consumable["per_batch"] == pytest.approx(75.0 * 1.2506 + nitrogen * 28.014, abs=0.5)
    degas = next(o for o in _yaml("process/recipe.yaml")["unit_procedures"][0]["operations"] if o["id"] == "degas")
    assert "nitrogen sweep" in degas["title"]


def test_phosgene_is_stripped_into_the_gas_not_boiled_off(model):
    """Finding 3: the dissolved phosgene's release is y = x p*(T) / P, at the table's x and MTSR."""
    design, readme = _text("DESIGN.md"), _text("README.md")
    for text in (design, readme, _text("process.yaml")):
        for phrase in ("boil off", "boils off", "0.8 K below", "0.8 K above"):
            assert phrase not in text, phrase
    for x, t, y in ((0.0014, 279.5, 0.0013), (0.0050, 282.9, 0.0053), (0.017, 294.4, 0.027)):
        assert x * _psat(model, "COCL2", t) / P_ATM == pytest.approx(y, rel=0.1), t
    for figure in ("0.11 kg/h (y 0.13 %)", "0.55 kg/h (y 0.53 %)", "7.3 kg/h (y 2.7 %, 1.8 m3/h)", "y = x p*(T) / P"):
        assert figure in design, figure
    # the scrubber's normal design load: the phosgene the dosing's vent gas strips, against the
    # balance's S28
    s28 = _kg(model, "S28")["COCL2"]
    assert 0.1 / s28 == pytest.approx(40, rel=0.15)
    assert "phosgene design load" in design


def test_stated_numbers_follow_from_the_flowsheet(model):
    """Finding 4: the purge, the charge's hexane per kg, the crude's and the distilled Boc2O."""
    design = _text("DESIGN.md")
    assert f"S36, {_state(model, 'S36')['flow']['value']:.3f} kg/h" in design
    per_kg = _kg(model, "S5")["HEX"] / _state(model, "S25")["flow"]["value"]
    assert f"{per_kg:.2f}" == "7.94"
    assert "(7.94 kg per kg of product)" in design and "7.94 kg/kg" in _text("process.yaml")
    alkoxide = _kmol(model, "S1")["KOTBU"]
    formed = _kmol(model, "S10")["BOC2O"] - _kmol(model, "S5")["BOC2O"]
    assert f"{100 * 2 * formed / alkoxide:.1f} %" == "91.1 %"
    assert "91.1 % of the alkoxide in the crude" in design
    distilled = _kmol(model, "S25")["BOC2O"]
    assert f"{distilled:.4f}" == "0.2892"
    assert "0.2892 kmol/h of Boc2O is distilled" in design
    assert 2 * distilled / alkoxide == pytest.approx(0.894, abs=5e-4)


def test_source_ids_name_the_register_row_they_cite():
    """Finding 5: every SRC-n in the YAML names the register row of the source it quotes."""
    import re

    register = {}
    for line in (PROCESS / "DESIGN.md").read_text(encoding="utf-8").splitlines():
        if m := re.match(r"\| (SRC-\d+) \| (.+?) \|", line):
            register[m.group(1)] = line
    assert "CoolProp" in register["SRC-9"] and "NIST" in register["SRC-9"]
    assert "Di-tert-butyl dicarbonate" in register["SRC-5"] and "Potassium chloride" in register["SRC-6"]
    for rel in ("process/materials.yaml", "process/flowsheet.yaml", "lca/lca.yaml"):
        text = " ".join((PROCESS / rel).read_text(encoding="utf-8").split())
        for m in re.finditer(r"SRC-(\d+)", text):
            sid = m.group(0)
            assert sid in register, (rel, sid)
            window = text[max(0, m.start() - 110) : m.start()]
            window = window.rsplit("SRC-", 1)[-1]
            row = register[sid]
            if "Wikipedia" in window:
                assert "| Wikipedia," in row, (rel, sid, window)
                if "Boc2O" in window or "56-57 C" in window:
                    assert sid == "SRC-5", (rel, sid, window)
                if "KCl" in window:
                    assert sid == "SRC-6", (rel, sid, window)
            if "NIST" in window:
                assert "NIST" in row, (rel, sid, window)
            if "CoolProp" in window:
                assert "CoolProp" in row, (rel, sid, window)
            if "chemicals" in window and "Wikipedia" not in window:
                assert "chemicals" in row, (rel, sid, window)
    materials = {c["id"]: c for c in _yaml("process/materials.yaml")["components"]}
    assert "SRC-5" in materials["BOC2O"]["vapour_pressure"]["source"]
    storage = next(e for e in _yaml("lca/lca.yaml")["emission_exclusions"] if e["id"] == "product-storage")
    assert "SRC-5" in storage["reason"]


def test_reboilers_deliver_the_boil_up_at_the_stills_end():
    """Finding 6: U A dT at the still's end covers the boil-up the still assumes for its run."""
    import re

    steps = {s["id"]: s for s in _yaml("process/flowsheet.yaml")["steps"]}
    pattern = re.compile(
        r"about (\d+) m2 at U (\d+) W/\(m2 K\)\) on hot water at (\d+)/(\d+) K: (\d+) kW at the end "
        r"of the [a-z ]+ \(([\d.]+) K, ([\d.]+) K below the water's mean ([\d.]+) K\)"
    )
    for sid in ("ST101", "ST301"):
        boilup = steps[sid]["still"]["boilup"]
        m = pattern.search(boilup["source"])
        assert m, sid
        area, u, hot, cold, kw, t_end, dt, mean = (float(g) for g in m.groups())
        assert mean == pytest.approx((hot + cold) / 2)
        assert dt == pytest.approx(mean - t_end, abs=0.05)
        assert u * area * dt / 1000 == pytest.approx(kw, abs=0.6)
        assert u * area * dt / 1000 >= boilup["value"], sid
    assert "about 27 m2" in _text("DESIGN.md") and "about 27 m2" in _text("equipment/equipment-list.yaml")
