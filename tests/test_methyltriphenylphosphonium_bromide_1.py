"""methyltriphenylphosphonium-bromide-1 (#133): the folder's hand-written numbers against its model.

Fast, without core: the flowsheet's calculated streams (written by cheme process propagate) and
the materials' molar masses, heat capacities and vapour pressures are enough to check what the
folder states by hand (DESIGN.md D-004, D-007..D-012):

- the duties written as hand arithmetic (Q1, Q5, Q6, Q8, Q9: the still's heat-up and metal, Q10:
  R-101's metal) follow from the streams they name, and the models' duties (Q2, Q3, Q7, written
  by propagate at each step's energy_port since core 1.9.0) match the streams too (Q7 the
  latent heat of the distillate S19);
- core 1.9.0 (D-015): the recycle is the tear S11 with its flow held as the wash ratio, the
  models' duties are calculated at their energy_port and the split-off parts keep the totals
  typed before, the default MTT at the vessel's pressure is below T_p so the hand MTT stays, R101
  has no vent and states no vent capacity, and plant.yaml requires 1.9;
- every energy flow reaches the LCI (library ADR 0035): LP steam, cooling water and brine per kg
  are the sums of their energy streams, as process.yaml and DESIGN.md state them;
- the jacket's coolant temperature is the cooling water's log-mean equivalent, not its supply,
  and the heating media stay below the stated temperature limits;
- the assumed temperatures of the charge (with the PPh3's heat of solution), the wash, the still
  feed and the vent header are the adiabatic mixes of their inlets;
- the hand splits DG101 and E201 and the recycle splitter X101 balance by component;
- the closed vessel's MTT (hazard.mtt) is the temperature at the relief's set pressure;
- the charge ratios (20 wt% PPh3, 1.05 mol methyl bromide per mol PPh3 in R-101) hold;
- the yield and assay stated hold and carry their caveat;
- the recipe's batch size times its batches per year gives the flowsheet's product rate;
- the process is public with CC-BY-4.0, every library entry is (ADR 0036).
"""

from __future__ import annotations

import csv
import math
import re
from pathlib import Path

import pytest
import yaml

KIT = Path(__file__).resolve().parents[1]
PROCESS = KIT / "processes" / "methyltriphenylphosphonium-bromide-1"


def _yaml(rel: str) -> dict:
    return yaml.safe_load((PROCESS / rel).read_text(encoding="utf-8"))


def _text(rel: str) -> str:
    return " ".join((PROCESS / rel).read_text(encoding="utf-8").split())


@pytest.fixture(scope="module")
def model():
    materials = {c["id"]: c for c in _yaml("process/materials.yaml")["components"]}
    flowsheet = _yaml("process/flowsheet.yaml")
    streams = {s["id"]: s for s in flowsheet["streams"]}
    steps = {s["id"]: s for s in flowsheet["steps"]}
    return materials, streams, steps


def _state(model, sid: str) -> dict:
    return model[1][sid]["state"]["design"]


def _kmol(model, sid: str) -> dict[str, float]:
    """kmol/h of each component of a material stream."""
    materials = model[0]
    state = _state(model, sid)
    flow = state["flow"]["value"]
    comp = state["composition"]
    if comp["basis"] == "mole_fraction":
        mm = sum(x * materials[k]["molar_mass"] for k, x in comp["values"].items())
        return {k: flow / mm * x for k, x in comp["values"].items()}
    return {k: flow * w / materials[k]["molar_mass"] for k, w in comp["values"].items()}


def _kg(model, sid: str) -> dict[str, float]:
    return {k: v * model[0][k]["molar_mass"] for k, v in _kmol(model, sid).items()}


def _mcp(model, sid: str) -> float:
    """kJ/(K h) of a stream from the components' liquid heat capacities."""
    return sum(n * model[0][k]["liquid_heat_capacity"] for k, n in _kmol(model, sid).items() if n)


def _t(model, sid: str) -> float:
    return _state(model, sid)["temperature"]["value"]


def _flow(model, sid: str) -> float:
    return _state(model, sid)["flow"]["value"]


def _duty(model, qid: str) -> float:
    return _state(model, qid)["duty"]["value"]


def _cycle(model) -> float:
    recipe = _yaml("process/recipe.yaml")
    return recipe["batch_size"]["value"] / _flow(model, "S15")


def _psat(model, cid: str, t: float) -> float:
    """kPa: the component's Antoine vapour pressure (log10 bar) of process/materials.yaml."""
    vp = model[0][cid]["vapour_pressure"]
    return 10 ** (vp["a"] - vp["b"] / (t + vp["c"])) * 100


def test_charge_ratios(model):
    s1, s3, s5, s6 = (_kmol(model, s) for s in ("S1", "S3", "S5", "S6"))
    pph3_kg = _kg(model, "S5")["PPH3"]
    assert _kg(model, "S5")["TOL"] / pph3_kg == pytest.approx(4.0, rel=1e-3)  # 20 wt% PPh3
    assert (s5["MEBR"] + s6["MEBR"]) / s5["PPH3"] == pytest.approx(1.05, rel=1e-3)
    assert s1["PPH3"] * _cycle(model) == pytest.approx(3.0, rel=1e-3)  # kmol a batch (D-004)
    # the recycled methyl bromide; both calculated, to the six digits propagate writes
    assert s5["MEBR"] == pytest.approx(s3["MEBR"], rel=1e-5)


def test_hand_duties_follow_the_streams(model):
    cycle = _cycle(model)
    metal_r101 = 3000.0 * 20.0 / cycle
    q1 = (_mcp(model, "S4") * (333.15 - _t(model, "S4")) + metal_r101) / 3600
    assert _duty(model, "Q1") == pytest.approx(q1, rel=2e-3)
    s5, s7 = _kmol(model, "S5"), _kmol(model, "S7")
    extent = s7["MTPPB"] + s7["MTPPB_S"] - s5.get("MTPPB", 0.0)
    q2 = (extent * 100_000 - _mcp(model, "S6") * 35.0) / 3600
    assert _duty(model, "Q2") == pytest.approx(q2, rel=2e-3)  # R101's model (core 1.9.0)
    cr101 = model[2]["CR101"]["crystallizer"]["energy"]["heat_capacity"]
    q3 = _flow(model, "S7") * cr101 * 20.0 / 3600  # CR101's lumped duty, its model (core 1.9.0)
    assert _duty(model, "Q3") == pytest.approx(q3, rel=2e-3)
    assert _duty(model, "Q10") == pytest.approx(metal_r101 / 3600, rel=2e-3)  # R-101's metal
    # CR101's heat capacity is the slurry's from the components (D-007)
    assert cr101 == pytest.approx(_mcp(model, "S7") / _flow(model, "S7"), abs=0.005)
    s18 = _kmol(model, "S18")
    q5 = (_flow(model, "S16") * 391.0 + _mcp(model, "S16") * 65.0 + (s18["TOL"] * 104.0 + s18["MEBR"] * 42.4) * 65.0) / 3600
    assert _duty(model, "Q5") == pytest.approx(q5, rel=2e-3)
    q6 = (_mcp(model, "S15") * (333.15 - _t(model, "S15")) + 4000.0 * (333.15 - _t(model, "S13")) / cycle) / 3600
    assert _duty(model, "Q6") == pytest.approx(q6, rel=2e-3)
    # Q7: the still's boil-up, its model's (core 1.9.0): the latent heat of the distillate S19 at
    # the components' heats of vaporization, 414.7 kWh a batch (cheme process stills)
    s19 = _kmol(model, "S19")
    latent = sum(n * model[0][k]["heat_of_vaporization"] for k, n in s19.items() if n)
    assert _duty(model, "Q7") == pytest.approx(latent / 3600, rel=1e-4)
    boil_kwh = _duty(model, "Q7") * cycle
    assert boil_kwh == pytest.approx(414.7, abs=0.05)
    # Q9: what the still leaves out, the charge to its bubble point and C-101's metal
    src = _state(model, "Q9")["duty"]["source"]
    t0 = float(re.search(r"to its bubble point ([0-9.]+) K", src).group(1))
    t1 = float(re.search(r"to the end's ([0-9.]+) K", src).group(1))
    q9 = (_mcp(model, "S17") * (t0 - _t(model, "S17")) + 2500.0 * (t1 - _t(model, "S17")) / cycle) / 3600
    assert _duty(model, "Q9") == pytest.approx(q9, rel=2e-3)
    q8 = (latent + _mcp(model, "S19") * ((t0 + t1) / 2 - _t(model, "S19"))) / 3600
    assert _duty(model, "Q8") == pytest.approx(q8, rel=2e-3)
    # the condenser takes what the boil-up gives (a total condenser): latent heat ~ boil-up
    assert latent == pytest.approx(boil_kwh * 3600 / cycle, rel=0.01)


def test_every_energy_flow_reaches_the_lci(model):
    _, streams, _ = model
    energy = [s for s in streams.values() if s.get("kind") == "energy"]
    by = {}
    for s in energy:
        end = s["from"] if s["from"].split(".")[0] in ("LPS", "POWER") else s["to"]
        by.setdefault(end.split(".")[0], set()).add(s["id"])
    assert by == {"LPS": {"Q1", "Q4", "Q7", "Q9"}, "CW": {"Q2", "Q3", "Q6", "Q8", "Q10"}, "BRINE": {"Q5"}, "POWER": {"P1", "P2", "P3"}}
    prod = _flow(model, "S15")
    per_kg = {k: sum(_duty(model, q) for q in v) / prod for k, v in by.items()}
    assert per_kg["LPS"] == pytest.approx(0.767, abs=0.0006)
    assert per_kg["CW"] == pytest.approx(0.703, abs=0.0006)
    assert per_kg["BRINE"] == pytest.approx(0.042, abs=0.0006)
    assert per_kg["POWER"] == pytest.approx(0.150, abs=0.0006)
    with (PROCESS / "lca" / "inventory.csv").open(encoding="utf-8", newline="") as handle:
        inventory = {row["key"]: row for row in csv.DictReader(handle)}
    for key, kind in (("feed:LPS", "LPS"), ("product:CW", "CW"), ("product:BRINE", "BRINE"), ("feed:POWER", "POWER")):
        assert float(inventory[key]["quantity"]) == pytest.approx(per_kg[kind], rel=1e-3), key
    for rel in ("process.yaml", "DESIGN.md"):
        text = _text(rel)
        for value in ("0.767 kWh", "0.703 kWh", "0.042 kWh", "0.150 kWh"):
            assert value in text, (rel, value)


def test_jacket_on_the_log_mean_and_heating_below_the_limits(model):
    recipe = _yaml("process/recipe.yaml")
    react = next(u for u in recipe["unit_procedures"] if u["id"] == "REACT")
    jacket = react["vessel"]["jacket"]
    t_p, t_in, t_out = 333.15, 298.15, 308.15
    lmtd = ((t_p - t_in) - (t_p - t_out)) / math.log((t_p - t_in) / (t_p - t_out))
    assert jacket["coolant_temperature"] == pytest.approx(t_p - lmtd, abs=0.01)
    mtt = model[2]["R101"]["hazard"]["mtt"]
    melting = 503.65  # the salt, chemicals 1.5.2 Tm (DESIGN.md D-008)
    assert jacket["heating_temperature"] < mtt < melting
    steam = _yaml("process/flowsheet.yaml")["feeds"]
    lps = next(f for f in steam if f["id"] == "LPS")["utility"]["supply_temperature"]["value"]
    assert lps < melting  # the still's steam


def test_assumed_temperatures_are_the_adiabatic_mixes(model):
    pph3 = _kmol(model, "S1")["PPH3"]
    num = sum(_mcp(model, s) * _t(model, s) for s in ("S1", "S2", "S3")) - pph3 * 20_000
    t4 = num / sum(_mcp(model, s) for s in ("S1", "S2", "S3"))
    assert _t(model, "S4") == pytest.approx(t4, abs=0.02)
    tw = (_mcp(model, "S9") * _t(model, "S9") + _mcp(model, "S11") * _t(model, "S11")) / (_mcp(model, "S9") + _mcp(model, "S11"))
    for sid in ("S12", "S13", "S14"):
        assert _t(model, sid) == pytest.approx(tw, abs=0.02), sid
    assert model[2]["W101"]["crystallizer"]["temperature"] == pytest.approx(tw, abs=0.02)
    t17 = sum(_mcp(model, s) * _t(model, s) for s in ("S10", "S14", "S16")) / sum(_mcp(model, s) for s in ("S10", "S14", "S16"))
    assert _t(model, "S17") == pytest.approx(t17, abs=0.02)
    gas = {"TOL": 104.0, "MEBR": 42.4}
    g = {s: sum(n * gas[k] for k, n in _kmol(model, s).items()) for s in ("S23", "S18")}
    t24 = (g["S23"] * _t(model, "S23") + g["S18"] * _t(model, "S18")) / sum(g.values())
    assert _t(model, "S24") == pytest.approx(t24, abs=0.02)
    assert _yaml("process/simulation.yaml")["specs"]["W101"]["mode"] == "adiabatic"


def test_hand_splits_balance_by_component(model):
    for inlet, outlets in (("S8", ("S22", "S23")), ("S21", ("S16", "S18")), ("S19", ("S3", "S11"))):
        before = _kg(model, inlet)
        after: dict[str, float] = {}
        for sid in outlets:
            for k, v in _kg(model, sid).items():
                after[k] = after.get(k, 0.0) + v
        for k in set(before) | set(after):
            assert after.get(k, 0.0) == pytest.approx(before.get(k, 0.0), abs=0.02 + 1e-3 * _flow(model, inlet)), (inlet, k)
    # DG101 takes 90 % of the slurry's methyl bromide (D-007); E201 all of the vapour's
    assert _kmol(model, "S23")["MEBR"] / _kmol(model, "S8")["MEBR"] == pytest.approx(0.9, rel=1e-4)
    assert _kmol(model, "S18")["MEBR"] == pytest.approx(_kmol(model, "S21")["MEBR"], rel=1e-4)


def _rho_toluene(t: float) -> float:
    """kg/m3: toluene's liquid density, a quadratic fit to thermo 0.11 over 290-440 K (max 0.09 %)."""
    return 1058.135 - 0.41517 * t - 8.0830e-4 * t * t


def _mtt(model, accumulation: float) -> tuple[float, float, float]:
    """K, kPa(a), kPa(a): the closed R-101's MTT at the end of the dosing (D-011).

    The temperature at which the vessel reaches its 700 kPa(a) relief set pressure, with
    ``accumulation`` of the batch's methyl bromide unreacted: Raoult's law over the liquid plus
    the nitrogen pad (230 kPa(a) at 333.15 K on the headspace before the dose), compressed by the
    dose's volume and by the toluene's thermal expansion. Also returns the pad and the pressure at
    T_p, both at the end of the dosing.
    """
    materials = model[0]
    cycle = _cycle(model)
    ch = {k: v * cycle for k, v in _kmol(model, "S5").items()}
    dose = _kmol(model, "S6")["MEBR"] * cycle
    mebr = accumulation * (ch["MEBR"] + dose)
    reacted = ch["MEBR"] + dose - mebr
    liquid = {"TOL": ch["TOL"], "MEBR": mebr, "PPH3": ch["PPH3"] - reacted}
    tol_kg = ch["TOL"] * materials["TOL"]["molar_mass"]
    # the other components and the dose at their liquid_molar_volume (20 C), the toluene at T
    others = sum(n * materials[k]["liquid_molar_volume"] for k, n in ch.items() if k != "TOL")
    v_dose = dose * materials["MEBR"]["liquid_molar_volume"]
    v_pad = 6.3 - tol_kg / _rho_toluene(333.15) - others  # the headspace the pad is set on

    def v_gas(t: float) -> float:
        return 6.3 - tol_kg / _rho_toluene(t) - others - v_dose

    total = sum(liquid.values())

    def pressure(t: float) -> float:
        nitrogen = 230.0 * v_pad / v_gas(t) * t / 333.15
        return nitrogen + sum(liquid[k] / total * _psat(model, k, t) for k in ("TOL", "MEBR"))

    low, high = 340.0, 500.0  # bisection: the pressure rises with the temperature
    while high - low > 1e-4:
        mid = (low + high) / 2
        low, high = (mid, high) if pressure(mid) < 700.0 else (low, mid)
    return (low + high) / 2, 230.0 * v_pad / v_gas(333.15), pressure(333.15)


def test_mtt_of_the_closed_vessel(model):
    """D-011: the temperature at which R-101 reaches 700 kPa(a) at the end of the dosing.

    The liquid's thermal expansion compresses the pad: leaving it out (the headspace fixed at
    its 333 K volume) gave 430.99 K, 16 K too high.
    """
    mtt, pad, p_tp = _mtt(model, 0.147)  # the screening's largest accumulation
    assert model[2]["R101"]["hazard"]["mtt"] == pytest.approx(mtt, abs=0.05)
    assert mtt == pytest.approx(415.29, abs=0.05)
    assert pad == pytest.approx(255.8, abs=0.1)
    assert p_tp == pytest.approx(281.8, abs=0.3)
    design = _text("DESIGN.md")
    assert "415.29 K" in design and "430.99 K, 16 K too high" in design
    for rel in ("README.md", "process.yaml"):
        assert "415.3 K" in _text(rel) and "431.0 K" not in _text(rel), rel
    assert "MTT 415.29 K" in _text("process/recipe.yaml")
    assert _rho_toluene(333.15) == pytest.approx(830.1, abs=0.2)  # thermo 0.11: 829.8
    # inside the fitted ranges of the vapour pressures: no extrapolation
    for cid in ("TOL", "MEBR"):
        low, high = model[0][cid]["vapour_pressure"]["temperature_range"]
        assert low < mtt < high, cid


@pytest.mark.parametrize(
    ("case", "accumulation", "stated"),
    [("k/10", 0.420, "409.12 K"), ("k/100", 0.850, "401.33 K"), ("nothing reacted", 1.0, "399.04 K")],
)
def test_mtt_of_each_sensitivity_case_is_its_own(model, case, accumulation, stated):
    """D-011: each case's MTT by the same method, and its MTSR below it (379 K for nothing reacted)."""
    mtt, _, _ = _mtt(model, accumulation)
    assert mtt == pytest.approx(float(stated.split()[0]), abs=0.05), case
    design = _text("DESIGN.md")
    assert stated in design, case
    mtsr = {"k/10": 351.7, "k/100": 371.9, "nothing reacted": 333.15 + 46.0}[case]
    assert mtsr < mtt
    assert mtt < model[0]["TOL"]["vapour_pressure"]["temperature_range"][1]
    assert "422.70 K" not in design and "412.47 K" not in design and "below 412 K" not in design


def test_yield_and_assay_as_stated_with_their_caveat(model):
    product = _kmol(model, "S15")
    yield_pph3 = product["MTPPB_S"] / _kmol(model, "S1")["PPH3"]
    assert yield_pph3 == pytest.approx(0.985, abs=0.0005)
    assay = _kg(model, "S15")["MTPPB_S"] / _flow(model, "S15")
    assert assay == pytest.approx(0.9987, abs=0.00005)
    description = " ".join(_yaml("process.yaml")["description"].split())
    assert "98.5 % on PPh3" in description and "99.87 wt%" in description
    assert "ASSUMED upper bounds" in description
    assert "ASSUMED upper bounds" in _text("DESIGN.md") and "ASSUMED upper bounds" in _text("README.md")
    assert "upper bound" in _yaml("process/design-basis.yaml")["products"][0]["purity"]
    # the source not read is not cited as read
    assert "not read" in _text("DESIGN.md").split("SRC-3")[1][:400]


def test_per_kg_feeds_as_stated(model):
    prod = _flow(model, "S15")
    assert _flow(model, "S1") / prod == pytest.approx(0.744, abs=0.0005)
    assert _flow(model, "S6") / prod == pytest.approx(0.281, abs=0.0005)
    assert _flow(model, "S2") / prod == pytest.approx(0.056, abs=0.0005)
    assert _flow(model, "S24") / prod == pytest.approx(0.022, abs=0.0005)
    assert _flow(model, "S20") / prod == pytest.approx(0.060, abs=0.0005)


def test_recipe_basis_and_capacity(model):
    recipe = _yaml("process/recipe.yaml")
    rate = _flow(model, "S15")
    batches = rate * recipe["hours_per_year"]["value"] / recipe["batch_size"]["value"]
    assert batches == pytest.approx(776.6, abs=0.1)
    assert rate * recipe["hours_per_year"]["value"] / 1000 == pytest.approx(820.9, abs=0.1)
    assert _cycle(model) == pytest.approx(10.198, abs=0.001)
    for rel in ("process.yaml", "DESIGN.md", "README.md"):
        assert "776.6" in _text(rel) and "820.9" in _text(rel), rel


def test_published_public_with_cc_by():
    publication = _yaml("process.yaml")["publication"]
    assert publication == {"status": "public", "license": "CC-BY-4.0"}


def test_lca_scope_states_the_recipe_basis_and_the_streams_it_uses(model):
    """lca/lca.yaml and lca/dataset.yaml carry the recipe's batch basis, the vent header S24 and
    the methyl bromide content of the liquors the streams give."""
    recipe = _yaml("process/recipe.yaml")
    batch = recipe["batch_size"]["value"]
    batches = _flow(model, "S15") * recipe["hours_per_year"]["value"] / batch
    lca_text = (PROCESS / "lca" / "lca.yaml").read_text(encoding="utf-8")
    lca = yaml.safe_load(lca_text)
    stated = f"{batch:.2f} kg per batch, {batches:.1f} batches a year"
    assert stated in lca["technology"]
    assert f"multiply by {batch:.2f} kg" in " ".join(lca_text.split())
    assert stated in _text("lca/dataset.yaml")
    assert "1057.09" not in lca_text and "775.9" not in _text("lca/dataset.yaml")
    # the OFFGAS exchange is the whole vent header S24 (S23 + S18), as inventory.csv carries it
    flows = {f["key"]: f for f in lca["flows"]}
    assert flows["product:OFFGAS"]["source"].startswith("flowsheet stream S24")
    with (PROCESS / "lca" / "inventory.csv").open(encoding="utf-8") as handle:
        inventory = {row["key"]: row for row in csv.DictReader(handle)}
    assert inventory["product:OFFGAS"]["streams"] == "S24"
    # the nitrogen has a disposal exchange, and the comment says so
    assert "disposal:consumable.nitrogen" in inventory
    assert "no disposal exchange" not in " ".join(lca_text.split())
    # the tanks hold the liquors' and the recovered toluene's methyl bromide, about 0.05 wt%
    for sid in ("S19", "S3", "S11"):
        w = _kg(model, sid)["MEBR"] / _flow(model, sid)
        assert w == pytest.approx(0.0005, abs=0.00005), sid
    breathing = next(e for e in lca["emission_exclusions"] if e["id"] == "tank-breathing")
    assert "about 0.05 wt% methyl bromide" in breathing["reason"]


def test_hand_sources_state_the_numbers_they_use(model):
    """The vacuum condenser's brine reason and the still feed's mixing arithmetic (D-010, D-009)."""
    vp = model[0]["TOL"]["vapour_pressure"]
    dew = vp["b"] / (vp["a"] - math.log10(0.05)) - vp["c"]  # K at 5 kPa(a)
    assert dew == pytest.approx(303.6, abs=0.1)
    assert _psat(model, "TOL", 268.15) == pytest.approx(0.65, abs=0.01)
    assert dew > 298.15  # cooling water cannot condense it usefully: brine
    q5 = _state(model, "Q5")["duty"]["source"]
    assert "about 304 K" in q5 and "290 K" not in q5
    design = _text("DESIGN.md")
    assert "5 kPa(a) is about 304 K" in design and "only below about 290 K" not in design
    assert _t(model, "S16") == pytest.approx(268.15)
    s17 = _state(model, "S17")["temperature"]["source"]
    assert f"S16 ({_mcp(model, 'S16'):.2f} at {_t(model, 'S16'):.2f} K)" in s17


# core 1.9.0 (DESIGN.md D-015)


def test_recycle_is_the_tear_s11_with_its_flow_held(model):
    """D-006: propagate converges the recycle's composition at S11 (ADR 0060), and S3 is X101's
    remainder; S11's flow (the wash ratio, a design input), the fresh feeds and the cycle stay
    set by hand, and the hand splits DG101 and E201 follow the converged S8 and S21."""
    flowsheet = _yaml("process/flowsheet.yaml")
    assert [t["stream"] for t in flowsheet["tears"]] == ["S11"]
    assert flowsheet["convergence"]["method"] == "wegstein"
    assert flowsheet["convergence"]["tolerance"]["abs"] <= 1e-6  # the six digits are the fixed point's
    s11, s3 = _state(model, "S11"), _state(model, "S3")
    assert s11["flow"]["provenance"] == "assumed"
    assert s11["composition"]["provenance"] == "calculated"
    assert "(tear, wegstein)" in s11["composition"]["source"]
    for name in ("flow", "composition"):
        assert s3[name]["provenance"] == "calculated", name
    # the wash ratio: 1 kg of recovered toluene per kg of salt in the cake (D-008)
    assert _flow(model, "S11") == pytest.approx(_kg(model, "S9")["MTPPB_S"], rel=1e-3)
    # the converged loop reproduces the hand-converged recycle (302.99 kg/h, 0.05 wt% methyl bromide)
    assert _flow(model, "S3") == pytest.approx(302.99, abs=0.005)
    assert _kg(model, "S3")["MEBR"] / _flow(model, "S3") == pytest.approx(0.00050077, rel=1e-4)
    text = _text("DESIGN.md")
    assert "L-5 (resolved in core 1.9.0, ADR 0060)" in text
    assert "converged by hand" not in _text("README.md")
    assert "converged by hand" not in " ".join(_yaml("process.yaml")["validation"]["notes"].split())
    assert "converged by hand" not in " ".join(" ".join(_yaml("process/design-basis.yaml")["assumptions"]).split())
    # what stays set by hand is named, S11's flow among it (README.md, D-006)
    for rel in ("README.md", "DESIGN.md"):
        assert "S11's flow (1 kg per kg of salt in S9" in _text(rel), rel
    # the hand splits follow the converged S8 and S21 to their written digits (D-007, D-008)
    s8, s21, s23, s18 = (_kg(model, s) for s in ("S8", "S21", "S23", "S18"))
    assert s23["MEBR"] == pytest.approx(0.9 * s8["MEBR"], rel=5e-6)
    assert s18["MEBR"] == pytest.approx(s21["MEBR"], rel=5e-6)
    s22, s16 = _kg(model, "S22"), _kg(model, "S16")
    for k in s8:
        assert s22.get(k, 0.0) + s23.get(k, 0.0) == pytest.approx(s8[k], rel=2e-6, abs=2e-6), k
    for k in s21:
        assert s16.get(k, 0.0) + s18.get(k, 0.0) == pytest.approx(s21[k], rel=2e-6, abs=2e-6), k


def test_model_duties_at_their_energy_port_and_the_split_off_parts(model):
    """D-010, D-015: the semi-batch, the crystallizer and the still write their duties (ADR 0059);
    what they leave out is its own assumed stream, and the totals are those typed until 1.8.0."""
    steps = model[2]
    for node, port, q in (("R101", "q", "Q2"), ("CR101", "q", "Q3"), ("ST101", "steam", "Q7")):
        assert steps[node]["energy_port"] == port, node
        stream = model[1][q]
        assert node in (stream["from"].split(".")[0], stream["to"].split(".")[0])
        assert port in (stream["from"].split(".")[1], stream["to"].split(".")[1])
        assert _state(model, q)["duty"]["provenance"] == "calculated", q
    for q in ("Q9", "Q10"):
        assert _state(model, q)["duty"]["provenance"] == "assumed", q
    assert model[1]["Q9"]["to"] == "ST101.steam_heatup"
    assert model[1]["Q10"]["from"] == "CR101.q_vessel"
    # the values the models now hold, and the totals typed until core 1.8.0
    assert _duty(model, "Q3") == pytest.approx(3.55153, abs=1e-5)
    assert _duty(model, "Q3") + _duty(model, "Q10") == pytest.approx(5.1858, abs=2e-4)
    assert _duty(model, "Q7") == pytest.approx(40.6685, abs=1e-4)
    # the still's boil-up exact rather than from 414.7 kWh rounded: 0.0045 kW more
    assert _duty(model, "Q7") + _duty(model, "Q9") - 60.6279 == pytest.approx(0.0045, abs=2e-4)
    assert _duty(model, "Q2") == pytest.approx(7.8775, abs=1e-4)
    design = _text("DESIGN.md")
    for stated in ("Q7 40.6685 kW", "Q9 19.964 kW", "Q3 3.5515 kW", "Q10 1.634 kW", "5.1858 against 3.55153 kW"):
        assert stated in design, stated


def test_default_mtt_at_the_vessels_pressure_is_below_t_p_so_the_hand_mtt_stays(model):
    """D-011, D-015: core 1.9.0's default MTT (ADR 0058) at 230 kPa(a) is its Clausius-Clapeyron
    estimate of pure methyl bromide's boiling point with the 384 K heat of vaporization; the
    entry's vapour pressure gives 300.0 K; both below T_p: the closed vessel's hand MTT stays."""
    mebr = model[0]["MEBR"]
    pressure = _state(model, "S5")["pressure"]["value"]  # R101's 230 kPa(a)
    t_p = _t(model, "S5")
    inv = 1 / mebr["normal_boiling_point"] - 8.314 * math.log(pressure / 101.325) / mebr["heat_of_vaporization"]
    default = 1 / inv
    assert default == pytest.approx(307.3, abs=0.05)
    assert default < t_p
    # the boiling point by the entry's vapour pressure (Antoine, bar, inside its 270-420 K range)
    vp = mebr["vapour_pressure"]
    antoine = vp["b"] / (vp["a"] - math.log10(pressure / 100.0)) - vp["c"]
    assert antoine == pytest.approx(300.0, abs=0.05)
    assert vp["temperature_range"][0] <= antoine <= vp["temperature_range"][1]
    assert antoine < default < t_p
    # not left out as a dissolved gas: above 5 mol% of the charge and doses
    cycle = _cycle(model)
    charge = {k: v * cycle for k, v in _kmol(model, "S5").items()}
    dose = _kmol(model, "S6")["MEBR"] * cycle
    share = (charge["MEBR"] + dose) / (sum(charge.values()) + dose)
    assert share == pytest.approx(0.078, abs=0.0005) and share > 0.05
    hazard = model[2]["R101"]["hazard"]
    assert hazard["mtt"] == pytest.approx(415.29)
    assert "307.3 K" in hazard["source"]
    assert "300.0 K" in hazard["source"]
    for rel in ("DESIGN.md", "README.md", "process.yaml"):
        assert "307.3 K" in _text(rel), rel
        assert "300.0 K" in _text(rel), rel


def test_r101_has_no_vent_and_states_no_vent_capacity(model):
    """D-015: R101 is closed while it reacts and QUAT forms no gas: no gas release to compare."""
    r101 = model[2]["R101"]
    assert "vent" not in r101["batch"]
    assert "vent_capacity" not in r101["hazard"]
    assert [p["direction"] for p in r101["ports"] if p.get("kind") != "energy"] == ["in", "in", "out"]
    reactions = _yaml("process/reactions.yaml")["reactions"]
    quat = next(r for r in reactions if r["id"] == "QUAT")
    products = {k for k, v in quat["stoichiometry"].items() if v > 0}
    assert products == {"MTPPB"}
    assert "no gas release" in _text("DESIGN.md")


def test_plant_requires_core_1_9():
    plant = _yaml("plant.yaml")
    assert plant["requires"] == "cheme-as-code>=1.9"
    comment = (PROCESS / "plant.yaml").read_text(encoding="utf-8")
    assert "1.9.0" in comment and "tears" in comment and "energy_port" in comment
