"""methyltriphenylphosphonium-bromide-1 (#133): the folder's hand-written numbers against its model.

Fast, without core: the flowsheet's calculated streams (written by cheme process propagate) and
the materials' molar masses, heat capacities and vapour pressures are enough to check what the
folder states by hand (DESIGN.md D-004, D-007..D-012):

- the duties written as hand arithmetic (Q1, Q5, Q6, Q8) follow from the streams they name, and
  the models' duties (Q2, Q3, Q7, written by propagate at each step's energy_port since core
  1.9.0) match the streams too (Q7 the latent heat of the distillate S19, the charge's heat-up
  and C-101's metal; Q3 the slurry's cool-down and R-101's metal, core 1.10.0);
- core 1.9.0 (D-015): the recycle is the tear S11 with its flow held as the wash ratio, the
  models' duties are calculated at their energy_port, the default MTT at the vessel's pressure is
  below T_p so the hand MTT stays, R101 has no vent and states no vent capacity;
- core 1.10.0 (D-016): the still's heat_up and the recipe vessels' metal put the former hand
  streams Q9 and Q10 into Q7 and Q3 (the same totals), the jacket times hold the metal, C-101 is
  sized by the recipe, the still's heat-up time is the hand operation at its boil-up rate, the
  agitators follow the occupancies, the column and the vent features are not used, and
  plant.yaml requires 1.10;
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


# the still's bubble point at the start and its end temperature (cheme process stills, D-009)
T_BUBBLE, T_END = 383.50, 386.48
METAL_R101, METAL_C101 = 3000.0, 2500.0  # kJ/K, ASSUMED (D-010), on the recipe's vessels


def _procedure(pid: str) -> dict:
    return next(u for u in _yaml("process/recipe.yaml")["unit_procedures"] if u["id"] == pid)


# the R10 preferred numbers (ISO 3) of one decade, the sizes core rounds a vessel up to (ADR 0052)
R10 = (1.0, 1.25, 1.6, 2.0, 2.5, 3.15, 4.0, 5.0, 6.3, 8.0)


def _r10(volume: float) -> float:
    """m3: the smallest R10 size at or above *volume* (1 to 100 m3)."""
    return next(r * d for d in (1.0, 10.0) for r in R10 if r * d >= volume)


def _batch_volume(model, sid: str) -> float:
    """m3 a batch of a stream's liquid: its kmol times the liquid_molar_volume of
    process/materials.yaml (ideal mixing, as core sizes a recipe vessel) times the cycle."""
    return sum(n * model[0][k]["liquid_molar_volume"] for k, n in _kmol(model, sid).items() if n) * _cycle(model)


def _jacket_hours(model, sid: str, medium: float, start: float, end: float, metal: float) -> float:
    """h to heat or cool R-101's content by the jacket (core's t = C / (U A) ln((T_m - T_0) /
    (T_m - T_1)), the medium constant), C the content's heat capacity a batch (stream *sid*) plus
    *metal*, A the shell and flat bottom the content wets in the 6.3 m3 vessel (H/D 1.2)."""
    vessel = _procedure("REACT")["vessel"]
    diameter = (4 * 6.3 / (math.pi * vessel["aspect_ratio"])) ** (1 / 3)
    bottom = math.pi * diameter**2 / 4
    area = math.pi * diameter * _batch_volume(model, sid) / bottom + bottom
    capacity = _mcp(model, sid) * _cycle(model) + metal  # kJ/K a batch
    return capacity / (vessel["jacket"]["u"] * area / 1000) * math.log((medium - start) / (medium - end)) / 3600


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
    metal_r101 = METAL_R101 * 20.0 / cycle  # kJ/h: R-101's metal over 20 K each batch
    # Q1 by hand: the metal from the 313.15 K the previous cool-down left it at (D-010, D-016)
    q1 = (_mcp(model, "S4") * (333.15 - _t(model, "S4")) + metal_r101) / 3600
    assert _duty(model, "Q1") == pytest.approx(q1, rel=2e-3)
    s5, s7 = _kmol(model, "S5"), _kmol(model, "S7")
    extent = s7["MTPPB"] + s7["MTPPB_S"] - s5.get("MTPPB", 0.0)
    q2 = (extent * 100_000 - _mcp(model, "S6") * 35.0) / 3600
    assert _duty(model, "Q2") == pytest.approx(q2, rel=2e-3)  # R101's model (core 1.9.0)
    cr101 = model[2]["CR101"]["crystallizer"]["energy"]["heat_capacity"]
    # Q3, CR101's model: its lumped duty (core 1.9.0) and R-101's metal cooled with it (1.10.0)
    q3 = (_flow(model, "S7") * cr101 * 20.0 + metal_r101) / 3600
    assert _duty(model, "Q3") == pytest.approx(q3, rel=2e-3)
    # CR101's heat capacity is the slurry's from the components (D-007)
    assert cr101 == pytest.approx(_mcp(model, "S7") / _flow(model, "S7"), abs=0.005)
    s18 = _kmol(model, "S18")
    q5 = (_flow(model, "S16") * 391.0 + _mcp(model, "S16") * 65.0 + (s18["TOL"] * 104.0 + s18["MEBR"] * 42.4) * 65.0) / 3600
    assert _duty(model, "Q5") == pytest.approx(q5, rel=2e-3)
    q6 = (_mcp(model, "S15") * (333.15 - _t(model, "S15")) + 4000.0 * (333.15 - _t(model, "S13")) / cycle) / 3600
    assert _duty(model, "Q6") == pytest.approx(q6, rel=2e-3)
    # Q7, ST101's model: the boil-up's latent heat of the distillate S19 at the components' heats
    # of vaporization, 414.7 kWh a batch (core 1.9.0), plus since core 1.10.0 the charge S17 to
    # its bubble point (heat_up) and C-101's metal from S17's temperature to the end's
    s19 = _kmol(model, "S19")
    latent = sum(n * model[0][k]["heat_of_vaporization"] for k, n in s19.items() if n)
    assert latent * cycle / 3600 == pytest.approx(414.7, abs=0.05)
    heat_up = _mcp(model, "S17") * (T_BUBBLE - _t(model, "S17"))
    metal = METAL_C101 * (T_END - _t(model, "S17")) / cycle
    assert _duty(model, "Q7") == pytest.approx((latent + heat_up + metal) / 3600, rel=2e-4)
    # Q8 by hand: the condenser takes the boil-up's latent heat, and the distillate is cooled
    q8 = (latent + _mcp(model, "S19") * ((T_BUBBLE + T_END) / 2 - _t(model, "S19"))) / 3600
    assert _duty(model, "Q8") == pytest.approx(q8, rel=2e-3)


def test_every_energy_flow_reaches_the_lci(model):
    _, streams, _ = model
    energy = [s for s in streams.values() if s.get("kind") == "energy"]
    by = {}
    for s in energy:
        end = s["from"] if s["from"].split(".")[0] in ("LPS", "POWER") else s["to"]
        by.setdefault(end.split(".")[0], set()).add(s["id"])
    assert by == {"LPS": {"Q1", "Q4", "Q7"}, "CW": {"Q2", "Q3", "Q6", "Q8"}, "BRINE": {"Q5"}, "POWER": {"P1", "P2", "P3"}}
    prod = _flow(model, "S15")
    per_kg = {k: sum(_duty(model, q) for q in v) / prod for k, v in by.items()}
    assert per_kg["LPS"] == pytest.approx(0.767, abs=0.0006)
    assert per_kg["CW"] == pytest.approx(0.703, abs=0.0006)
    assert per_kg["BRINE"] == pytest.approx(0.042, abs=0.0006)
    assert per_kg["POWER"] == pytest.approx(0.154, abs=0.0006)
    with (PROCESS / "lca" / "inventory.csv").open(encoding="utf-8", newline="") as handle:
        inventory = {row["key"]: row for row in csv.DictReader(handle)}
    for key, kind in (("feed:LPS", "LPS"), ("product:CW", "CW"), ("product:BRINE", "BRINE"), ("feed:POWER", "POWER")):
        assert float(inventory[key]["quantity"]) == pytest.approx(per_kg[kind], rel=1e-3), key
    for rel in ("process.yaml", "DESIGN.md"):
        text = _text(rel)
        for value in ("0.767 kWh", "0.703 kWh", "0.042 kWh", "0.154 kWh"):
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


def test_model_duties_at_their_energy_port(model):
    """D-010, D-015, D-016: the semi-batch, the crystallizer and the still write their duties
    (ADR 0059), calculated, at their energy_port; since core 1.10.0 nothing they leave out of the
    vessels' metal and the still's heat-up is on a hand stream any more."""
    steps = model[2]
    for node, port, q in (("R101", "q", "Q2"), ("CR101", "q", "Q3"), ("ST101", "steam", "Q7")):
        assert steps[node]["energy_port"] == port, node
        stream = model[1][q]
        assert node in (stream["from"].split(".")[0], stream["to"].split(".")[0])
        assert port in (stream["from"].split(".")[1], stream["to"].split(".")[1])
        assert _state(model, q)["duty"]["provenance"] == "calculated", q
    assert _duty(model, "Q2") == pytest.approx(7.8775, abs=1e-4)


# core 1.10.0 (DESIGN.md D-016)


def test_hand_streams_q9_and_q10_are_removed_with_their_ports(model):
    """The still's heat-up and C-101's metal (Q9) and R-101's metal (Q10) are in Q7 and Q3."""
    assert "Q9" not in model[1] and "Q10" not in model[1]
    flowsheet = _yaml("process/flowsheet.yaml")
    ports = {
        (node["id"], p["id"])
        for group in ("feeds", "products", "blocks", "steps")
        for node in flowsheet[group]
        for p in node.get("ports", [])
    }
    for gone in (("ST101", "steam_heatup"), ("CR101", "q_vessel"), ("RECOV", "steam2"), ("REACT", "cw3"), ("LPS", "st101_heatup"), ("CW", "cr101_vessel")):
        assert gone not in ports, gone
    lca = (PROCESS / "lca" / "lca.yaml").read_text(encoding="utf-8")
    assert "Q9" not in lca and "Q10" not in lca
    assert "(Q9, Q10)" not in _text("README.md")


def test_still_duty_holds_the_heat_up_and_the_metal(model):
    """ST101's `heat_up` and the RECOVER vessel's metal (ADR 0063): Q7 60.6328 kW, the boil-up
    40.6685, the charge to its bubble point 14.6525 and C-101's metal 5.3118 kW (cheme process
    stills), the hand Q7 + Q9 of core 1.9.0 (40.6685 + 19.9639) to their rounding."""
    assert model[2]["ST101"]["still"]["heat_up"] is True
    assert _procedure("RECOVER")["vessel"]["metal_heat_capacity"] == METAL_C101
    cycle = _cycle(model)
    boil = 414.7476850820376 / cycle  # kW: the boil-up's latent heat (cheme process stills)
    heat_up = _mcp(model, "S17") * (T_BUBBLE - _t(model, "S17")) / 3600
    metal = METAL_C101 * (T_END - _t(model, "S17")) / cycle / 3600
    assert boil == pytest.approx(40.6685, abs=1e-4)
    assert heat_up == pytest.approx(14.6525, abs=2e-3)
    assert metal == pytest.approx(5.3118, abs=5e-4)  # T_END rounded to 0.01 K
    assert _duty(model, "Q7") == pytest.approx(60.6328, abs=1e-4)
    assert _duty(model, "Q7") == pytest.approx(boil + heat_up + metal, abs=2e-3)
    assert _duty(model, "Q7") - (40.6685 + 19.9639) == pytest.approx(0.0004, abs=1e-4)
    # the still's 0.81 h heat-up operation: that heat to the bubble point at its 250 kW
    boilup = model[2]["ST101"]["still"]["boilup"]["value"]
    to_bubble = (heat_up * cycle + METAL_C101 * (T_BUBBLE - _t(model, "S17")) / 3600)  # kWh a batch
    assert to_bubble == pytest.approx(201.54, abs=0.05)
    op = next(o for o in _procedure("RECOVER")["operations"] if o["id"] == "heat")
    assert op["duration"]["value"] == pytest.approx(to_bubble / boilup, abs=0.005)
    design = _text("DESIGN.md")
    for stated in ("Q7 60.6328 kW", "14.6525 kW", "5.3118", "201.54 kWh", "0.81 h", "L-9"):
        assert stated in design, stated


def test_crystallizer_duty_holds_r101s_metal(model):
    """CR101's Q3 with the REACT vessel's 3000 kJ/K cooled by 20 K: 3.55153 + 1.63427 = 5.1858 kW,
    the hand Q10 (1.6342 kW) of core 1.9.0, and the typed Q3 of core 1.8.0."""
    assert _procedure("REACT")["vessel"]["metal_heat_capacity"] == METAL_R101
    metal = METAL_R101 * 20.0 / _cycle(model) / 3600
    assert metal == pytest.approx(1.63427, abs=1e-5)
    assert _duty(model, "Q3") == pytest.approx(5.1858, abs=1e-4)
    assert _duty(model, "Q3") - metal == pytest.approx(3.55153, abs=2e-5)
    assert metal == pytest.approx(1.6342, abs=1e-4)
    assert "Q3 5.1858 kW" in _text("DESIGN.md")


def test_jacket_times_hold_r101s_metal(model):
    """The heat and cool times use C + C_m (ADR 0063): from the jacket of recipe.yaml on the
    content's own heat capacity and wetted area, 0.535 and 0.552 h without the metal, times
    (C + 3000) / C, 0.789 and 0.807 h (cheme process recipe); with the recipe's fixed durations
    and R101's dose and post-reaction, R-101 is occupied 10.15 h of the 10.198 h cycle, under it
    by 0.05 h, and stays off the bottleneck (D-016)."""
    cycle = _cycle(model)
    up = _procedure("REACT")
    vessel, ops = up["vessel"], {o["id"]: o for o in up["operations"]}
    assert vessel["metal_heat_capacity"] == METAL_R101
    # the vessel core sizes: the larger of the charge (S5) and the end (S7), 4.435 m3, in 6.3 m3
    working = max(_batch_volume(model, "S5"), _batch_volume(model, "S7"))
    assert working == pytest.approx(4.435, abs=0.001)
    assert _r10(working / vessel["fill_fraction"]) == 6.3
    jacket = vessel["jacket"]
    times = {}
    for op, sid, medium in (("heat", "S5", jacket["heating_temperature"]), ("cool", "S7", jacket["coolant_temperature"])):
        start, end = ops[op]["temperatures"]
        alone = _jacket_hours(model, sid, medium, start, end, 0.0)
        times[op] = _jacket_hours(model, sid, medium, start, end, METAL_R101)
        content = _mcp(model, sid) * cycle
        assert times[op] == pytest.approx(alone * (content + METAL_R101) / content, rel=1e-9)
        assert times[op] - alone == pytest.approx(0.25, abs=0.01), op  # ADR 0063's quarter hour
    assert ops["heat"]["temperatures"] == [292.81, 333.15] and ops["cool"]["temperatures"] == [333.15, 313.15]
    assert times["heat"] == pytest.approx(0.789, abs=5e-4) and times["cool"] == pytest.approx(0.807, abs=5e-4)
    # R101's model: the 3 h dosing and the 2.30 h post-reaction (cheme process recipe, D-005)
    r101 = model[2]["R101"]["batch"]
    dose = sum(d["time"] for d in r101["dosing"]) / 3600
    fixed = sum(o["duration"]["value"] for o in ops.values() if "duration" in o)
    occupied = fixed + times["heat"] + times["cool"] + dose + 2.30
    assert occupied == pytest.approx(10.146, abs=0.005)
    assert cycle - occupied == pytest.approx(0.05, abs=0.01) and occupied < cycle
    # the recipe's heat report: R-101's metal from the charge's 292.81 K, 1.662 kW above the hand
    # Q1, whose metal starts at the 313.15 K the cool-down left (D-016)
    report_kw = (_mcp(model, "S4") * (333.15 - 292.81) * cycle + METAL_R101 * (333.15 - 292.81)) / cycle / 3600
    assert report_kw == pytest.approx(10.224, abs=0.002)
    assert report_kw - _duty(model, "Q1") == pytest.approx(METAL_R101 * (313.15 - 292.81) / cycle / 3600, abs=0.002)
    assert report_kw - _duty(model, "Q1") == pytest.approx(1.662, abs=0.002)
    design = _text("DESIGN.md")
    for stated in ("0.789 h", "0.807 h", "10.224 kW", "1.662 kW", "99.5 %"):
        assert stated in design, stated


def test_c101_sized_by_the_recipe(model):
    """L-1 resolved: the still's unit procedure gives a vessel (ADR 0063); the liquor it takes in a
    batch, S17's 4210.41 kg, is 4.852 m3 by the materials' molar volumes, in the R10 size 6.3 m3."""
    vessel = _procedure("RECOVER")["vessel"]
    assert vessel["fill_fraction"] == 0.8 and "volume" not in vessel
    assert model[1]["S17"]["to"] == "ST101.in"
    assert _flow(model, "S17") * _cycle(model) == pytest.approx(4210.41, abs=0.01)
    working = _batch_volume(model, "S17")
    assert working == pytest.approx(4.852, abs=5e-4)
    # the same within 2 % by toluene's density at the feed's temperature (most of the liquor)
    assert _flow(model, "S17") * _cycle(model) / _rho_toluene(_t(model, "S17")) == pytest.approx(working, rel=0.02)
    assert _r10(working / vessel["fill_fraction"]) == 6.3
    assert working / 6.3 == pytest.approx(0.77, abs=0.005)
    design = _text("DESIGN.md")
    assert "L-1 (resolved in core 1.10.0, ADR 0063)" in design
    assert "C-101 6.3 m3 (4.852 m3 of liquor" in design
    assert "4.852 m3" in _text("equipment/equipment-list.yaml")


def test_agitators_follow_the_occupancies(model):
    """P1 and P3 with R-101's 10.146 h and C-101's 3.469 h of the cycle (cheme process recipe)."""
    cycle = _cycle(model)
    p1 = 5.5 * 10.146 / cycle + 0.75 * 3.0 / cycle
    p3 = 3.0 * 3.469 / cycle + 2.0
    assert _duty(model, "P1") == pytest.approx(p1, abs=0.05)
    assert _duty(model, "P3") == pytest.approx(p3, abs=0.05)
    occupied = sum(o["duration"]["value"] for o in _procedure("RECOVER")["operations"] if "duration" in o) + 1.659
    assert occupied == pytest.approx(3.469, abs=0.001)
    assert "electricity 16.0 kW" in _text("DESIGN.md")


def test_column_and_vent_features_not_used(model):
    """D-016: one stage is the credible recovery (no still.column, purity or condenser_port) and
    R101 has no vent (no vent vapour, condenser or Henry split); each is recorded with its reason."""
    still = model[2]["ST101"]["still"]
    assert "column" not in still and "condenser_port" not in still
    assert "distilled" in still["end"] and "purity" not in still["end"]
    for node in model[2].values():
        assert "vent" not in node.get("batch", {}), node["id"]
        assert all("heat_of_solution" not in d for d in node.get("batch", {}).get("dosing", []))
    design = _text("DESIGN.md")
    for stated in ("`still.column`, ADR 0061", "`still.condenser_port` (ADR 0061)", "`batch.vent.vapour`", "a dose's `heat_of_solution` (ADR 0063)"):
        assert stated in design, stated
    # Q8's latent part is the still's boil-up term of Q7 (a condenser_port would write that alone):
    # Q8 less the distillate S19 cooled from the still's mean temperature equals Q7 less the
    # charge's heat-up and C-101's metal
    s19 = _kmol(model, "S19")
    latent = sum(n * model[0][k]["heat_of_vaporization"] for k, n in s19.items() if n) / 3600
    assert latent == pytest.approx(40.669, abs=0.001)
    cooled = _mcp(model, "S19") * ((T_BUBBLE + T_END) / 2 - _t(model, "S19")) / 3600
    heat_up = _mcp(model, "S17") * (T_BUBBLE - _t(model, "S17")) / 3600
    metal = METAL_C101 * (T_END - _t(model, "S17")) / _cycle(model) / 3600
    boil_term = _duty(model, "Q7") - heat_up - metal
    assert _duty(model, "Q8") - cooled == pytest.approx(boil_term, abs=1e-3)
    assert _duty(model, "Q8") - cooled == pytest.approx(latent, abs=1e-3)


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


def test_plant_requires_core_1_10():
    plant = _yaml("plant.yaml")
    assert plant["requires"] == "cheme-as-code>=1.10"
    comment = (PROCESS / "plant.yaml").read_text(encoding="utf-8")
    assert "1.9.0" in comment and "tears" in comment and "energy_port" in comment
    assert "1.10.0" in comment and "heat_up" in comment and "metal_heat_capacity" in comment
